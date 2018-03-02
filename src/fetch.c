/*-------------------------------------------------------------------------
 *
 * fetch.c
 *    Functions for fetching files from PostgreSQL data directory
 *
 * Portions Copyright (c) 1996-2017, PostgreSQL Global Development Group
 *
 *-------------------------------------------------------------------------
 */

#include "postgres_fe.h"

#include "catalog/catalog.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#include "pg_probackup.h"

/*
 * Read a file into memory. The file to be read is <datadir>/<path>.
 * The file contents are returned in a malloc'd buffer, and *filesize
 * is set to the length of the file.
 *
 * The returned buffer is always zero-terminated; the size of the returned
 * buffer is actually *filesize + 1. That's handy when reading a text file.
 * This function can be used to read binary files as well, you can just
 * ignore the zero-terminator in that case.
 *
 */
char *
slurpFile(const char *datadir, const char *path, size_t *filesize, bool safe)
{
	int		 fd;
	char	   *buffer;
	struct stat statbuf;
	char		fullpath[MAXPGPATH];
	int		 len;
	snprintf(fullpath, sizeof(fullpath), "%s/%s", datadir, path);

	if ((fd = open(fullpath, O_RDONLY | PG_BINARY, 0)) == -1)
	{
		if (safe)
			return NULL;
		else
			elog(ERROR, "could not open file \"%s\" for reading: %s",
					fullpath, strerror(errno));
	}

	if (fstat(fd, &statbuf) < 0)
	{
		if (safe)
			return NULL;
		else
			elog(ERROR, "could not open file \"%s\" for reading: %s",
				fullpath, strerror(errno));
	}

	len = statbuf.st_size;

	buffer = pg_malloc(len + 1);

	if (read(fd, buffer, len) != len)
	{
		if (safe)
			return NULL;
		else
			elog(ERROR, "could not read file \"%s\": %s\n",
				fullpath, strerror(errno));
	}

	close(fd);

	/* Zero-terminate the buffer. */
	buffer[len] = '\0';

	if (filesize)
		*filesize = len;
	return buffer;
}

/*
 * Receive a single file as a malloc'd buffer.
 */
char *
fetchFile(PGconn *conn, const char *filename, size_t *filesize)
{
	PGresult   *res;
	char	   *result;
	const char *params[1];
	int			len;

	params[0] = filename;
	res = pgut_execute(conn, "SELECT pg_catalog.pg_read_binary_file($1)",
					   1, params, false);

	/* sanity check the result set */
	if (PQntuples(res) != 1 || PQgetisnull(res, 0, 0))
		elog(ERROR, "unexpected result set while fetching remote file \"%s\"",
			 filename);

	/* Read result to local variables */
	len = PQgetlength(res, 0, 0);
	result = pg_malloc(len + 1);
	memcpy(result, PQgetvalue(res, 0, 0), len);
	result[len] = '\0';

	PQclear(res);
	*filesize = len;

	return result;
}
