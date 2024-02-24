from dataclasses import asdict, astuple

from sqlalchemy import insert, select, exists, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmailSettings
from app.data.models import UserEmailSettings as EmailSettingsDB


class EmailSettingsDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
     

    async def update(self, user_id: int, **kwargs) -> None:
        query = update(EmailSettingsDB).where(EmailSettingsDB.user_id == user_id).values(**kwargs)

        await self.session.execute(query)
        await self.session.commit()
      

    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(EmailSettingsDB, key) == value for key, value in kwargs.items() if hasattr(EmailSettingsDB, key))
        ))

        result = await self.session.execute(query)

        return result.scalar_one()


    async def add(self, email_settings: EmailSettings) -> None:
        query = insert(EmailSettingsDB).values(**asdict(email_settings))
        await self.session.execute(query)
        await self.session.commit()


    async def get_one(self, **kwargs) -> EmailSettings:
        exists = await self.exists(**kwargs)
        
        if not exists:
            return None
        
        query = select(EmailSettingsDB).filter_by(**kwargs)

        results = await self.session.execute(query)

        db_email = results.scalar_one()

        return EmailSettings(
            quantity=db_email.quantity,
            schedule_time=db_email.schedule_time,
            email_subject=db_email.email_subject,
            email_text=db_email.email_text,
            user_id=db_email.user_id
            
        )


    async def get_all(self, **kwargs) -> list[EmailSettings]:
        exists = await self.exists(**kwargs)
        
        if not exists:
            return None
        
        query = select(EmailSettingsDB).filter_by(**kwargs)

        results = await self.session.execute(query)

        db_emails = results.scalars().all()

        # settings = [EmailSettings(
        #         quantity=db_email.quantity,
        #         schedule_time=db_email.schedule_time,
        #         email_subject=db_email.email_subject,
        #         email_text=db_email.email_text,
        #         user_id=db_email.user_id
        #     ) for db_email in db_emails
        # ]

        # return astuple(settings)

        return [
            EmailSettings(
                quantity=db_email.quantity,
                schedule_time=db_email.schedule_time,
                email_subject=db_email.email_subject,
                email_text=db_email.email_text,
                user_id=db_email.user_id
            ) for db_email in db_emails
        ]
