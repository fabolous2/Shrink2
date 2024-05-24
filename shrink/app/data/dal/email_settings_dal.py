from dataclasses import asdict

from sqlalchemy import and_, delete, insert, select, exists, update
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
        print(email_settings)
        email_settings_dict = {
            'user_id': email_settings.user_id,
            'email_subject': email_settings.email_subject,
            'email_text': email_settings.email_text,
            'amount': email_settings.amount,
            'schedule_time': email_settings.schedule_time,
            'frequency': email_settings.frequency,
            'current_frequency': email_settings.current_frequency,
            'email_limit_to_send': email_settings.email_limit_to_send, 
            'advice_for_frequency': email_settings.advice_for_frequency,
            'advice_for_quantity': email_settings.advice_for_quantity,
            'email_limit_to_send_for_extra': email_settings.email_limit_to_send_for_extra
        }
        query = insert(EmailSettingsDB).values(**email_settings_dict)
        await self.session.execute(query)
        await self.session.commit()
        
    
    async def delete(self, **kwargs) -> None:
        # Построение списка условий для WHERE
        conditions = [
            getattr(EmailSettingsDB, key) == value
            for key, value in kwargs.items()
            if hasattr(EmailSettingsDB, key)
        ]
        
        # Собираем все условия с использованием and_()
        query = delete(EmailSettingsDB).where(and_(*conditions))

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
            amount=db_email.amount,
            schedule_time=db_email.schedule_time,
            email_subject=db_email.email_subject,
            email_text=db_email.email_text,
            user_id=db_email.user_id,
            is_turned_on=db_email.is_turned_on,
            frequency=db_email.frequency,
            current_frequency=db_email.current_frequency,
            email_limit_to_send=db_email.email_limit_to_send, 
            email_limit_to_send_for_extra=db_email.email_limit_to_send_for_extra,
            advice_for_frequency=db_email.advice_for_frequency,
            advice_for_quantity=db_email.advice_for_quantity
        )


    async def get_all(self, **kwargs) -> list[EmailSettings]:
        exists = await self.exists(**kwargs)
        
        if not exists:
            return None
        
        query = select(EmailSettingsDB).filter_by(**kwargs)

        results = await self.session.execute(query)

        db_emails = results.scalars().all()

        return [
            EmailSettings(
                amount=db_email.amount,
                schedule_time=db_email.schedule_time,
                email_subject=db_email.email_subject,
                email_text=db_email.email_text,
                user_id=db_email.user_id,
                is_turned_on=db_email.is_turned_on,
                email_limit_to_send=db_email.email_limit_to_send,
                email_limit_to_send_for_extra = db_email.email_limit_to_send_for_extra
            ) for db_email in db_emails
        ]
