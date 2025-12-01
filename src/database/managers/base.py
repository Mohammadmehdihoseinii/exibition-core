
class ManagerBase:
    def __init__(self, db):
        self.db = db

    def get_session(self):
        return self.db.get_session()

    def save(self, session, instance, add=True, refresh=True, commit=True, close=True):
        if add:
            session.add(instance)

        if commit:
            session.commit()

        if refresh:
            session.refresh(instance)

        if close:
            session.close()

        return instance