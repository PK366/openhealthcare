GitHub Actions CI
=================

This page describes the GitHub Actions test and quality-check workflows for
Care. It is intended for contributors investigating CI runs and maintaining
the pipeline. It does not describe or authorize deployments to any environment.

Test pipeline
-------------

The reusable test workflow runs on an ARM64 GitHub-hosted runner and uses the
following Compose files:

* `docker-compose.yaml`
* `docker-compose.local.yaml`
* `docker-compose.ci.yaml`

The workflow builds the development image, starts the Compose services, checks
for missing database migrations, validates fixtures, and runs the backend
test suite with coverage. The workflow also attempts to reuse Docker build
cache between eligible runs.

The test workflow has a 90-minute job timeout. A timeout or failed step is
reported in the corresponding GitHub Actions run; inspect the failed step
before retrying.

Artifacts
---------

The workflow may publish these artifacts:

+----------------------+----------------------+----------------------------------------------+
| Artifact             | Retention            | When it is produced                          |
+======================+======================+==============================================+
| `backend-coverage`  | 14 days              | Whenever the coverage file is available      |
+----------------------+----------------------+----------------------------------------------+
| `ci-diagnostics`    | 7 days               | On failure, after the redaction step succeeds|
+----------------------+----------------------+----------------------------------------------+
| `care-db-dump`      | 30 days              | On eligible pushes to the `develop` branch  |
+----------------------+----------------------+----------------------------------------------+

The Codecov upload is optional. If the `CODECOV_TOKEN` secret is not
configured for the workflow, the upload step is skipped; the backend coverage
artifact is still handled independently.

Failure diagnostics and redaction
---------------------------------

When a test job fails, the workflow collects Docker Compose service status and
the last 200 lines of service logs into the runner's temporary diagnostics
directory. Before an artifact can be uploaded, the workflow runs a redaction
step. That step also exercises its supported patterns against dummy values on
every test run.

The current self-tests cover common secret assignments, quoted API keys,
query-string credentials, Bearer tokens, URL credentials, private-key blocks,
AWS access keys, and GitHub token formats. The redaction step processes
diagnostic text files when they exist. The diagnostics artifact is uploaded
only when the job has failed and redaction completed successfully.

Redaction is a defensive safeguard, not a guarantee that every possible
secret format is detected. Do not intentionally place credentials, tokens,
private keys, or production data in CI logs. Review diagnostic artifacts
carefully and report any suspected exposure through the repository's
established security process.

Service cleanup
---------------

The test job always attempts to stop its Compose services and remove the
workflow's Compose volumes and orphaned containers, including after a failure.
This cleanup applies to the isolated GitHub Actions runner only. It does not
operate on a contributor's workstation, shared server, or UAT environment.

Troubleshooting checklist
-------------------------

#. Open the failed GitHub Actions run and identify the first failing step.
#. Review the step output and, when present, download the `ci-diagnostics`
   artifact from that run.
#. Check migration and fixture validation output before investigating test
   failures.
#. Confirm whether the optional Codecov step was skipped because the token
   was unavailable; this alone does not indicate a failed test run.
#. If diagnostics were not uploaded, check whether the job failed and whether
   the redaction step completed successfully.
#. After making a fix, rerun the relevant workflow and verify the new run's
   job and step conclusions.

Maintenance notes
-----------------

* Keep workflow permissions scoped to the minimum required by each job.
* Preserve the failure-only condition and successful-redaction dependency for
  diagnostics uploads.
* Keep redaction self-tests based exclusively on synthetic dummy values.
* Update this page whenever artifact names, retention periods, failure
  collection, redaction behavior, or cleanup behavior changes.
* Avoid changing application runtime configuration as part of CI-only
  maintenance unless that change is separately reviewed and approved.
