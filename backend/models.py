class StudySession:
    def __init__(self, subject_id, duration, notes):
        self.subject_id = subject_id
        self.duration = duration
        self.notes = notes

    def is_long_session(self):
        return self.duration >= 60
