# RazorFlow AI — Intelligent Agentic Commerce Platform

**Razorpay AI Buildathon (Track 1: AI Growth & Agentic Commerce)**

RazorFlow AI is an end-to-end autonomous e-commerce prototype that bridges natural language product discovery, budget-aware recommendations, stateful agentic workflows (LangGraph), human-in-the-loop payment execution guardrails, and Razorpay Checkout JS integration.

---

## 🏗️ Architecture

- **Frontend:** React SPA (Vite), React Router Dom, Tailwind CSS, Axios, and Razorpay Checkout JS SDK.
- **Backend:** FastAPI (Python) REST API.
- **Agent Engine:** LangGraph orchestrating tool execution (`search_catalog`, `manage_cart`, `create_razorpay_order`) and human-in-the-loop payment guardrails.
- **Payment Integration:** Razorpay Test Mode API (`razorpay-python` SDK) with SHA256 HMAC signature verification.

---

## ⚡ Quick Start

### 1. Start FastAPI Backend Server
```powershell
cd backend
python -m pip install -r requirements.txt
python -m app.main
```
> Backend runs at `http://127.0.0.1:8000`

### 2. Start React Frontend SPA
```powershell
cd frontend
npm install
npm run dev
```
> Frontend runs at `http://localhost:3000`

---

## 🎯 Key Routes

- `http://localhost:3000/` — Customer Conversational Agent Chat Interface
