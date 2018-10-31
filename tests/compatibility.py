import unittest
import subprocess
import os
from .helpers.ptrack_helpers import ProbackupTest, ProbackupException
from sys import exit

module_name = 'compatibility'


class CompatibilityTest(ProbackupTest, unittest.TestCase):

    # @unittest.expectedFailure
    # @unittest.skip("skip")
    def test_backward_compatibility_page(self):
        """Description in jira issue PGPRO-434"""
        fname = self.id().split('.')[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(
            base_dir="{0}/{1}/node".format(module_name, fname),
            set_replication=True,
            initdb_params=['--data-checksums'],
            pg_options={
                'max_wal_senders': '2',
                'autovacuum': 'off'}
            )
        self.init_pb(backup_dir, old_binary=True)
        self.show_pb(backup_dir)

        self.add_instance(backup_dir, 'node', node, old_binary=True)
        self.show_pb(backup_dir)

        self.set_archiving(backup_dir, 'node', node, old_binary=True)
        node.slow_start()

        node.pgbench_init(scale=10)

        # FULL backup with old binary
        self.backup_node(
            backup_dir, 'node', node, old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        self.show_pb(backup_dir)

        self.validate_pb(backup_dir)

        # RESTORE old FULL with new binary
        node_restored = self.make_simple_node(
            base_dir="{0}/{1}/node_restored".format(module_name, fname))

        node_restored.cleanup()

        self.restore_node(
                backup_dir, 'node', node_restored,
                options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Page BACKUP with old binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='page',
            old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()
        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Page BACKUP with new binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='page',
            options=['--log-level-file=verbose'])

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()

        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

    # @unittest.expectedFailure
    # @unittest.skip("skip")
    def test_backward_compatibility_delta(self):
        """Description in jira issue PGPRO-434"""
        fname = self.id().split('.')[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(
            base_dir="{0}/{1}/node".format(module_name, fname),
            set_replication=True,
            initdb_params=['--data-checksums'],
            pg_options={
                'max_wal_senders': '2',
                'autovacuum': 'off'}
            )
        self.init_pb(backup_dir, old_binary=True)
        self.show_pb(backup_dir)

        self.add_instance(backup_dir, 'node', node, old_binary=True)
        self.show_pb(backup_dir)

        self.set_archiving(backup_dir, 'node', node, old_binary=True)
        node.slow_start()

        node.pgbench_init(scale=10)

        # FULL backup with old binary
        self.backup_node(
            backup_dir, 'node', node, old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        self.show_pb(backup_dir)

        self.validate_pb(backup_dir)

        # RESTORE old FULL with new binary
        node_restored = self.make_simple_node(
            base_dir="{0}/{1}/node_restored".format(module_name, fname))

        node_restored.cleanup()

        self.restore_node(
                backup_dir, 'node', node_restored,
                options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Delta BACKUP with old binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='delta',
            old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()
        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Delta BACKUP with new binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='delta',
            options=['--log-level-file=verbose'])

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()

        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

    # @unittest.expectedFailure
    # @unittest.skip("skip")
    def test_backward_compatibility_ptrack(self):
        """Description in jira issue PGPRO-434"""
        fname = self.id().split('.')[3]
        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        node = self.make_simple_node(
            base_dir="{0}/{1}/node".format(module_name, fname),
            set_replication=True,
            initdb_params=['--data-checksums'],
            pg_options={
                'max_wal_senders': '2',
                'autovacuum': 'off'}
            )
        self.init_pb(backup_dir, old_binary=True)
        self.show_pb(backup_dir)

        self.add_instance(backup_dir, 'node', node, old_binary=True)
        self.show_pb(backup_dir)

        self.set_archiving(backup_dir, 'node', node, old_binary=True)
        node.slow_start()

        node.pgbench_init(scale=10)

        # FULL backup with old binary
        self.backup_node(
            backup_dir, 'node', node, old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        self.show_pb(backup_dir)

        self.validate_pb(backup_dir)

        # RESTORE old FULL with new binary
        node_restored = self.make_simple_node(
            base_dir="{0}/{1}/node_restored".format(module_name, fname))

        node_restored.cleanup()

        self.restore_node(
                backup_dir, 'node', node_restored,
                options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Delta BACKUP with old binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='delta',
            old_binary=True)

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()
        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)

        # Delta BACKUP with new binary
        pgbench = node.pgbench(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            options=["-c", "4", "-T", "20"]
        )
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(
            backup_dir, 'node', node, backup_type='delta',
            options=['--log-level-file=verbose'])

        if self.paranoia:
            pgdata = self.pgdata_content(node.data_dir)

        node_restored.cleanup()

        self.restore_node(
            backup_dir, 'node', node_restored,
            options=["-j", "4", "--recovery-target-action=promote"])

        if self.paranoia:
            pgdata_restored = self.pgdata_content(node_restored.data_dir)
            self.compare_pgdata(pgdata, pgdata_restored)
