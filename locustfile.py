from locust import HttpUser, task, between

class StudentUser(HttpUser):
    wait_time = between(1, 2)

    token = ".eJwVyzEOgCAMheG7dGahbozGxcHJAxjERhqlGsDBGO9uHd_38j_AC7gGDVxFwIFtB8R-tNiAAfGJ1IS3yHthWaPiQqfPNZFUvbioFAqVj7_udM2-hjjd5LMCIrwfsXQd8w.aDM0Pg.MJQtrI53nl3vgLGjYZOn36ecHdk"


    @task
    def get_student_quizzes(self):
        self.client.get("/student",
            headers={"Authorization": self.token}
        )

    # @task
    # def take_quiz(self):
    #     token = ".eJwVyzEOgCAMheG7dGahbozGxcHJAxjERhqlGsDBGO9uHd_38j_AC7gGDVxFwIFtB8R-tNiAAfGJ1IS3yHthWaPiQqfPNZFUvbioFAqVj7_udM2-hjjd5LMCIrwfsXQd8w.aCfsXQ.YY9FMdHr6iXfJdpvu2e-UwYYo_4"

    #     headers = {"Authorization": token}

    #     # Step 1: Simulate quiz loading
    #     self.client.get(
    #         "/student/get-quiz-details?quiz_id=14&quiz_name=TEST1",
    #         headers=headers
    #     )


