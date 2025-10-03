# Example Use (API In Project)

import asyncio
import requests
import time
from datetime import datetime
import json
import os
import sys

# Add API path (if not in the same folder)
sys.path.append('.')
from logger_api import project_logger


class MyProjectWithLogging:
    def __init__(self, project_name="my_test_project"):
        self.project_name = project_name
        self.logger = project_logger

        # Start Log
        self.logger.info(
            f"Project {project_name} started",
            tags=["startup", "init"],
            user_id=os.getenv('USER', 'unknown'),
            pid=os.getpid()
        )

    def process_data(self, data_list):
        try:
            self.logger.info(
                f"Start processing {len(data_list)} data items",
                tags=["processing", "data"],
                data_count=len(data_list)
            )

            processed = 0
            errors = 0

            for i, item in enumerate(data_list):
                try:
                    # Simulation
                    if item < 0:
                        raise ValueError(f"Illegal negative value: {item}")

                    result = item * 2 + 1
                    processed += 1

                    if item > 100:
                        self.logger.warning(
                            f"Large amount processed: {item}",
                            tags=["processing", "large_value"],
                            item_value=item,
                            result=result,
                            index=i
                        )

                except Exception as e:
                    errors += 1
                    self.logger.error(
                        f"Error processing item {i}: {str(e)}",
                        tags=["processing", "error"],
                        item_value=item,
                        index=i,
                        error_type=type(e).__name__
                    )

            # Summery
            if errors > 0:
                self.logger.warning(
                    f"Processing completed with {errors} errors",
                    tags=["processing", "completed", "with_errors"],
                    processed_count=processed,
                    error_count=errors,
                    total_count=len(data_list),
                    success_rate=f"{(processed / len(data_list) * 100):.1f}%"
                )
            else:
                self.logger.success(
                    f"Processing of {len(data_list)} items completed successfully",
                    tags=["processing", "completed", "success"],
                    processed_count=processed,
                    duration_seconds=time.time()
                )

            return processed, errors

        except Exception as e:
            self.logger.error(
                f"General error in data processing: {str(e)}",
                tags=["processing", "critical_error"],
                error_type=type(e).__name__,
                data_count=len(data_list) if data_list else 0
            )
            raise

    def connect_to_database(self, db_url="fake://database"):
        """Simulation Connect To DB"""
        try:
            self.logger.info(
                "Connecting to database...",
                tags=["database", "connection"],
                db_url=db_url
            )

            # sleep for connection
            time.sleep(2)

            # Emulation (Error)
            import random
            if random.random() < 0.3:  # 30%
                raise ConnectionError("Failed to connect to database.")

            self.logger.success(
                "Connection to database established.",
                tags=["database", "connected"],
                db_url=db_url,
                connection_time=2.0
            )

            return True

        except Exception as e:
            self.logger.error(
                f"Error connecting to database: {str(e)}",
                tags=["database", "connection_error"],
                db_url=db_url,
                error_type=type(e).__name__
            )
            return False

    def fetch_api_data(self, api_url="https://jsonplaceholder.typicode.com/posts/1"):  # Example
        try:
            self.logger.info(
                "Getting data from API...",
                tags=["api", "fetch"],
                api_url=api_url
            )

            start_time = time.time()
            response = requests.get(api_url, timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                self.logger.success(
                    "Data received from API",
                    tags=["api", "fetch", "success"],
                    api_url=api_url,
                    status_code=response.status_code,
                    response_time=f"{duration:.2f}s",
                    data_size=len(str(data))
                )
                return data
            else:
                self.logger.warning(
                    f"API returned error code {response.status_code}",
                    tags=["api", "fetch", "warning"],
                    api_url=api_url,
                    status_code=response.status_code,
                    response_time=f"{duration:.2f}s"
                )
                return None

        except requests.exceptions.Timeout:
            self.logger.error(
                "Timeout while receiving data from API",
                tags=["api", "fetch", "timeout"],
                api_url=api_url,
                timeout=10
            )
            return None

        except Exception as e:
            self.logger.error(
                f"Error getting data from API: {str(e)}",
                tags=["api", "fetch", "error"],
                api_url=api_url,
                error_type=type(e).__name__
            )
            return None

    def run_batch_job(self):
        job_start = time.time()
        job_id = f"job_{int(job_start)}"

        self.logger.info(
            f"Start job {job_id}",
            tags=["job", "batch", "start"],
            job_id=job_id,
            start_time=datetime.now().isoformat()
        )

        try:
            # 1 - connect to db
            if not self.connect_to_database():
                raise Exception("اتصال به دیتابیس ناموفق")

            # 2 - get data from api
            api_data = self.fetch_api_data()
            if not api_data:
                self.logger.warning(
                    "Data not retrieved from API, using sample data",
                    tags=["job", "fallback"],
                    job_id=job_id
                )

            # 3 - process Data
            test_data = [1, 5, -2, 150, 25, -1, 200, 30]
            processed, errors = self.process_data(test_data)

            # Summery job
            job_duration = time.time() - job_start

            if errors == 0:
                self.logger.success(
                    f"Job {job_id} completed successfully",
                    tags=["job", "batch", "completed", "success"],
                    job_id=job_id,
                    duration=f"{job_duration:.2f}s",
                    processed_items=processed,
                    total_errors=errors
                )
            else:
                self.logger.warning(
                    f"Job {job_id} completed but with {errors} errors",
                    tags=["job", "batch", "completed", "with_errors"],
                    job_id=job_id,
                    duration=f"{job_duration:.2f}s",
                    processed_items=processed,
                    total_errors=errors
                )

        except Exception as e:
            job_duration = time.time() - job_start
            self.logger.error(
                f"Job {job_id} failed: {str(e)}",
                tags=["job", "batch", "failed"],
                job_id=job_id,
                duration=f"{job_duration:.2f}s",
                error_type=type(e).__name__
            )
            raise

        finally:
            self.logger.info(
                f"End of job {job_id}",
                tags=["job", "batch", "end"],
                job_id=job_id,
                total_duration=f"{time.time() - job_start:.2f}s"
            )


def monitor_system_resources():
    """Manitoring"""
    import psutil

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        project_logger.warning(
            f"High CPU usage: {cpu_percent}%",
            tags=["system", "cpu", "high_usage"],
            cpu_percent=cpu_percent,
            threshold=80
        )

    # Memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        project_logger.warning(
            f"High RAM usage: {memory.percent}%",
            tags=["system", "memory", "high_usage"],
            memory_percent=memory.percent,
            available_gb=f"{memory.available / 1024 ** 3:.1f}",
            threshold=85
        )

    # Disk usage
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        project_logger.error(
            f"Low disk space: {disk.percent}% used",
            tags=["system", "disk", "critical"],
            disk_percent=disk.percent,
            free_gb=f"{disk.free / 1024 ** 3:.1f}",
            threshold=90
        )

    project_logger.debug(
        "System Resource Status",
        tags=["system", "monitoring"],
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_percent=disk.percent
    )


async def async_task_example():
    """Ex task async"""
    try:
        project_logger.info(
            "Start async task",
            tags=["async", "task", "start"]
        )

        # Simulation async
        for i in range(5):
            await asyncio.sleep(1)
            project_logger.debug(
                f"Step {i + 1} of async task",
                tags=["async", "task", "progress"],
                step=i + 1,
                total_steps=5
            )

        project_logger.success(
            "async task completed successfully",
            tags=["async", "task", "completed"]
        )

    except Exception as e:
        project_logger.error(
            f"Error in async task: {str(e)}",
            tags=["async", "task", "error"],
            error_type=type(e).__name__
        )


def main():
    """Main Function"""
    print("Starting logging system test...")

    # New Project
    project = MyProjectWithLogging("test_project_v2")

    try:
        # Various tests
        print("\n📊 Running batch job...")
        project.run_batch_job()

        print("\n🖥 Checking system resources...")
        monitor_system_resources()

        print("\n⚡ Running async task...")
        asyncio.run(async_task_example())

        # end log
        project_logger.success(
            "Logging system test completed successfully",
            tags=["test", "completed", "main"],
            timestamp=datetime.now().isoformat()
        )

        print("\nTest completed! Now you can see the logs in the Telegram bot.")

    except Exception as e:
        project_logger.error(
            f"Error executing test: {str(e)}",
            tags=["test", "error", "main"],
            error_type=type(e).__name__
        )
        raise


if __name__ == "__main__":
    main()