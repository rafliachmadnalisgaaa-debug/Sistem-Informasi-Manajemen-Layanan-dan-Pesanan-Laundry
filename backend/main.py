from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, date
import bcrypt
from jose import jwt
import hmac
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://ifvxixshzqoglosmwsmk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlmdnhpeHNoenFvZ2xvc213c21rIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzU3MTUwNywiZXhwIjoyMDk5MTQ3NTA3fQ.Zsuo-e_JM57stplUYb2tdDRqITQvqrD1MdrWinhLDWI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- KONFIGURASI KEAMANAN & SMTP ---
SECRET_KEY = "rahasia_rara_laundry_super_aman"
ALGORITHM = "HS256"
SIGNATURE_SECRET = b"rahasia_signature_api"

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "rafliachmadnalisgaaa@gmail.com"  # GANTI DENGAN EMAIL ANDA
SMTP_PASSWORD = "RafliAchmadN029"  # GANTI DENGAN APP PASSWORD GMAIL

app = FastAPI(title="Rara Laundry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mengizinkan frontend dari port manapun (mencegah error Failed to Fetch CORS)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UTILS ---
def send_otp_email(receiver_email: str, otp_code: str):
    print(f"\n=======================================================")
    print(f" [DEBUG OTP] KODE OTP UNTUK {receiver_email}: {otp_code}")
    print(f"=======================================================\n")
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = receiver_email
        msg['Subject'] = "OTP Registrasi Rara Laundry"
        body = f"Kode OTP Anda: {otp_code}\nBerlaku 10 menit."
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Gagal kirim email: {e}")
        print("-> SILAKAN GUNAKAN KODE OTP DI ATAS UNTUK MELANJUTKAN")

def verify_signature(request: Request, x_signature: str = Header(...)):
    expected = hmac.new(SIGNATURE_SECRET, request.url.path.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=403, detail="Invalid API Signature")

def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid Authentication")

# --- MODEL DATA ---
class UserReg(BaseModel): name: str; phone: str; address: str; email: EmailStr; password: str
class UserVerify(BaseModel): email: EmailStr; otp: str
class UserLog(BaseModel): email: EmailStr; password: str; remember_me: bool = False
class ServiceModel(BaseModel): name: str; type: str; price: float
class OrderModel(BaseModel): customer_name: str; service_id: int; weight_or_qty: float; is_delivery: bool; phone: Optional[str] = None; address: Optional[str] = None; status: Optional[str] = "proses"

# --- ENDPOINT AUTHENTICATION ---
@app.post("/auth/register")
def register(user: UserReg):
    if supabase.table("users").select("id").eq("email", user.email).execute().data:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    hashed_pw = get_password_hash(user.password)
    supabase.table("users").insert({
        "name": user.name, "phone": user.phone, "address": user.address,
        "email": user.email, "password_hash": hashed_pw, "is_verified": True
    }).execute()

    return {"message": "Registrasi berhasil."}

@app.post("/auth/login")
def login(user: UserLog):
    res = supabase.table("users").select("*").eq("email", user.email).execute().data
    if not res or not verify_password(user.password, res[0]["password_hash"]):
        raise HTTPException(status_code=400, detail="Email/Password salah")
    
    days = 30 if user.remember_me else 1
    token = jwt.encode({"sub": res[0]["id"], "exp": datetime.utcnow() + timedelta(days=days)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "name": res[0]["name"]}

# --- ENDPOINT SERVICES (CRUD) ---
@app.get("/services/")
def get_services(): return supabase.table("services").select("*").order("id").execute().data

@app.post("/services/", dependencies=[Depends(verify_signature)])
def create_service(srv: ServiceModel): return supabase.table("services").insert(srv.dict()).execute().data

@app.delete("/services/{id}", dependencies=[Depends(verify_signature)])
def delete_service(id: int): return supabase.table("services").delete().eq("id", id).execute().data

# --- ENDPOINT ORDERS (CRUD) ---
@app.get("/orders/")
def get_orders(search: Optional[str] = None, status: Optional[str] = None):
    q = supabase.table("orders").select("*, services(name)").order("created_at", desc=True)
    if search: q = q.ilike("customer_name", f"%{search}%")
    if status: q = q.eq("status", status)
    return q.execute().data

@app.post("/orders/", dependencies=[Depends(verify_signature)])
def create_order(order: OrderModel):
    today = datetime.now().strftime("%Y-%m-%d")
    queue = len(supabase.table("orders").select("id").gte("created_at", today).execute().data) + 1
    price = float(supabase.table("services").select("price").eq("id", order.service_id).execute().data[0]["price"])
    
    data = order.dict()
    data.update({"queue_number": queue, "total_price": price * order.weight_or_qty})
    return supabase.table("orders").insert(data).execute().data

@app.put("/orders/{id}", dependencies=[Depends(verify_signature)])
def update_order(id: str, status: str): 
    return supabase.table("orders").update({"status": status}).eq("id", id).execute().data

@app.delete("/orders/{id}", dependencies=[Depends(verify_signature)])
def delete_order(id: str): 
    return supabase.table("orders").delete().eq("id", id).execute().data

# --- ENDPOINT ABSENSI ---
@app.get("/attendance/status")
def check_attendance_status(authorization: str = Header(...)):
    user_id = get_current_user(authorization)
    user = supabase.table("users").select("email").eq("id", user_id).execute().data
    if not user: raise HTTPException(404, "User not found")
    today = datetime.now().strftime("%Y-%m-%d")
    existing = supabase.table("attendance").select("id").eq("user_email", user[0]["email"]).eq("checkin_date", today).execute().data
    return {"checked_in": len(existing) > 0}

@app.post("/attendance/checkin")
def checkin_attendance(authorization: str = Header(...)):
    user_id = get_current_user(authorization)
    user = supabase.table("users").select("email").eq("id", user_id).execute().data
    if not user: raise HTTPException(404, "User not found")
    today = datetime.now().strftime("%Y-%m-%d")
    existing = supabase.table("attendance").select("id").eq("user_email", user[0]["email"]).eq("checkin_date", today).execute().data
    if existing: raise HTTPException(status_code=400, detail="Anda sudah absen hari ini")
    supabase.table("attendance").insert({"user_email": user[0]["email"], "checkin_date": today}).execute()
    return {"message": "Berhasil absen!"}

@app.get("/attendance/summary")
def get_attendance_summary(authorization: str = Header(...)):
    user_id = get_current_user(authorization)
    user = supabase.table("users").select("email").eq("id", user_id).execute().data
    if not user: raise HTTPException(404, "User not found")
    now = datetime.now()
    first_day = f"{now.year}-{now.month:02d}-01"
    data = supabase.table("attendance").select("id").eq("user_email", user[0]["email"]).gte("checkin_date", first_day).execute().data
    
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    month_name = f"{months[now.month-1]} {now.year}"
    return {"total_days": len(data), "month_name": month_name}

# --- ENDPOINT LAPORAN SABTU ---
import csv
from io import StringIO
from fastapi.responses import PlainTextResponse

@app.get("/reports/saturday")
def download_saturday_report(authorization: str = Header(...)):
    get_current_user(authorization)
    if datetime.now().weekday() != 5: # 5 = Sabtu
        raise HTTPException(status_code=400, detail="Laporan hanya bisa didownload pada hari Sabtu!")
    
    orders = supabase.table("orders").select("*, services(name)").eq("status", "selesai").execute().data
    if not orders: raise HTTPException(status_code=400, detail="Tidak ada riwayat transaksi selesai")
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Tanggal", "Pelanggan", "Layanan", "Total Harga", "HP", "Alamat"])
    
    ids_to_del = []
    for o in orders:
        ids_to_del.append(o["id"])
        writer.writerow([o["id"], o["created_at"], o["customer_name"], o["services"]["name"] if o.get("services") else "", o["total_price"], o.get("phone", ""), o.get("address", "")])
        
    for oid in ids_to_del: supabase.table("orders").delete().eq("id", oid).execute()
        
    response = PlainTextResponse(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=riwayat_transaksi_sabtu.csv"
    return response