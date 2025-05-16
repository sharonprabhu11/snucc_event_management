import csv
import io
import random
import string
import qrcode
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import base64

from database import get_db, engine
import models
import schemas


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Tracker API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_identifier(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_qr_code(data, role="Attendee"):
    
    role_colors = {
        "organiser": ("white", "darkblue"),
        "speaker": ("black", "red"),
        "attendee": ("black", "yellow")  
    }

    fill_color, back_color = role_colors.get(role.lower(), ("black", "white"))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    buffer = io.BytesIO()
    img.save(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


@app.get("/")
def read_root():
    return {"message": "Welcome to Event Tracker API"}

@app.post("/upload-csv", response_model=schemas.AttendeeList)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        decoded_content = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_content))
        
        attendees = []
        skipped = 0
        for row in csv_reader:
            name = row.get('Name', '').strip()
            email = row.get('Email', '').strip().lower()
            phone = row.get('Phone', '').strip() if row.get('Phone') else None
            role = row.get('Role', 'Attendee').strip()

            if not name or not email:
                continue

            # Check for exact match
            existing_attendee = db.query(models.Attendee).filter(
                models.Attendee.email == email
            ).first()

            if existing_attendee:
                skipped += 1
                continue

            identifier = generate_identifier()
            while db.query(models.Attendee).filter(
                models.Attendee.identifier == identifier
            ).first():
                identifier = generate_identifier()

            attendee = models.Attendee(
                name=name,
                email=email,
                phone=phone,
                role=role,
                identifier=identifier,
                registered=False,
                lunch_collected=False,
                kit_collected=False
            )

            db.add(attendee)
            db.flush()
            attendees.append(attendee)
            
            db.commit()

        
        return {
            "attendees": attendees,
            "total_processed": len(attendees) + skipped,
            "added": len(attendees),
            "skipped": skipped
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.get("/attendees", response_model=List[schemas.AttendeeResponse])
def get_attendees(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    query = db.query(models.Attendee)
    
    if search:
        query = query.filter(
            (models.Attendee.name.contains(search)) |
            (models.Attendee.email.contains(search)) |
            (models.Attendee.identifier.contains(search))
        )
    
    attendees = query.offset(skip).limit(limit).all()
    return attendees

@app.get("/attendee/{identifier}", response_model=schemas.AttendeeResponse)
def get_attendee(identifier: str, db: Session = Depends(get_db)):
    attendee = db.query(models.Attendee).filter(models.Attendee.identifier == identifier).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return attendee

@app.put("/attendee/{identifier}", response_model=schemas.AttendeeResponse)
def update_attendee(identifier: str, attendee_update: schemas.AttendeeUpdate, db: Session = Depends(get_db)):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.identifier == identifier).first()
    if not db_attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    

    if attendee_update.registered is not None:
        if attendee_update.registered and not db_attendee.registered:
            db_attendee.registration_time = datetime.now()
        db_attendee.registered = attendee_update.registered
    
    if attendee_update.lunch_collected is not None:
        db_attendee.lunch_collected = attendee_update.lunch_collected
    
    if attendee_update.kit_collected is not None:
        db_attendee.kit_collected = attendee_update.kit_collected
    
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

@app.get("/qrcode/{identifier}")
def get_qrcode(identifier: str, db: Session = Depends(get_db)):
    attendee = db.query(models.Attendee).filter(models.Attendee.identifier == identifier).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    
    qr_code = generate_qr_code(identifier, attendee.role)
    return {
        "identifier": identifier,
        "name": attendee.name,
        "role": attendee.role,
        "qr_code": qr_code
    }


@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Attendee).count()
    registered = db.query(models.Attendee).filter(models.Attendee.registered == True).count()
    lunch_collected = db.query(models.Attendee).filter(models.Attendee.lunch_collected == True).count()
    kit_collected = db.query(models.Attendee).filter(models.Attendee.kit_collected == True).count()
    
    return {
        "total": total,
        "registered": registered,
        "lunch_collected": lunch_collected,
        "kit_collected": kit_collected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)