from datetime import datetime, timedelta

import pytest
from meltano.core.job import Job
from meltano.core.job.stale_job_failer import StaleJobFailer


class TestStaleJobFailer:
    @pytest.fixture
    def live_job(self, session):
        job = Job(job_id="test")
        job.start()
        job.save(session)

        return job

    @pytest.fixture
    def stale_job(self, session):
        job = Job(job_id="test")
        job.start()
        job.last_heartbeat_at = datetime.utcnow() - timedelta(minutes=10)
        job.save(session)

        return job

    @pytest.fixture
    def other_stale_job(self, session):
        job = Job(job_id="other")
        job.start()
        job.last_heartbeat_at = datetime.utcnow() - timedelta(minutes=10)
        job.save(session)

        return job

    @pytest.fixture
    def complete_job(self, session):
        job = Job(job_id="other")
        job.start()
        job.success()
        job.save(session)

        return job

    def test_fail_stale_jobs(
        self, live_job, stale_job, other_stale_job, complete_job, session
    ):
        assert stale_job.is_stale()
        assert other_stale_job.is_stale()

        failer = StaleJobFailer()
        failer.fail_stale_jobs(session)

        session.refresh(live_job)
        session.refresh(stale_job)
        session.refresh(other_stale_job)
        session.refresh(complete_job)

        # Leaves non-stale jobs alone
        assert live_job.is_running()
        assert complete_job.is_complete()

        # Marks all stale jobs as failed
        assert stale_job.has_error()
        assert not stale_job.is_stale()

        assert other_stale_job.has_error()
        assert not other_stale_job.is_stale()

    def test_fail_stale_jobs_with_job_id(
        self, live_job, stale_job, other_stale_job, complete_job, session
    ):
        assert stale_job.is_stale()
        assert other_stale_job.is_stale()

        failer = StaleJobFailer(job_id=stale_job.job_id)
        failer.fail_stale_jobs(session)

        session.refresh(live_job)
        session.refresh(stale_job)
        session.refresh(other_stale_job)
        session.refresh(complete_job)

        # Leaves non-stale jobs alone
        assert live_job.is_running()
        assert complete_job.is_complete()

        # Marks stale jobs with the job ID as failed
        assert stale_job.has_error()
        assert not stale_job.is_stale()

        # Leaves stale jobs with a different job ID alone
        assert other_stale_job.is_stale()
