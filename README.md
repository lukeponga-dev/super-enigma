# **Complete Guide: Starting a Tor Onion E-Commerce Site**  

This guide will walk you through setting up a **secure, anonymous e-commerce site** on the Tor network. We'll cover:  
1. **Legal Considerations**  
2. **Server Setup (Secure VPS + Tor Hidden Service)**  
3. **E-Commerce Platform (Simple vs. Advanced Options)**  
4. **Payment Processing (Bitcoin/Monero Only)**  
5. **Security & Anonymity Best Practices**  

---

## **⚠️ Legal Disclaimer**  
- **Tor is legal**, but selling illegal goods is not.  
- **Know your laws** (e.g., drugs, weapons, stolen data are illegal in most places).  
- **This guide is for educational purposes only.**  

---

# **Step 1: Secure Your Identity & Infrastructure**  
### **1.1 Use an Anonymous Operating System**  
- **Tails OS** (Live USB) or **Whonix** (Virtual Machine) for admin tasks.  
- Never access your server from a personal device.  

### **1.2 Get a Secure VPS (Paid in Crypto)**  
- **Recommended Providers:**  
  - Njalla (accepts Monero)  
  - 1984 Hosting (Iceland, privacy-focused)  
- **Payment:** Use **Monero (XMR)** or Bitcoin (BTC) via a non-KYC exchange.  

### **1.3 SSH Access Over Tor (No IP Leaks)**  
- Install `torsocks` and connect via:  
  ```bash
  torsocks ssh user@your-server-ip
  ```  
- **Disable password login** (use SSH keys only).  

---

# **Step 2: Install & Configure Tor Hidden Service**  
### **2.1 Install Tor**  
```bash
sudo apt update && sudo apt install tor
```  

### **2.2 Configure Hidden Service**  
Edit `/etc/tor/torrc`:  
```ini
HiddenServiceDir /var/lib/tor/your_ecom_site/  
HiddenServicePort 80 127.0.0.1:8080  # Forward .onion traffic to local port 8080
```  

### **2.3 Restart Tor & Get Onion Address**  
```bash
sudo systemctl restart tor  
sudo cat /var/lib/tor/your_ecom_site/hostname  
# Output: yourstorexyz.onion
```  

---

# **Step 3: Set Up the E-Commerce Site**  
### **Option A: Simple Static HTML Site (Most Secure)**  
- No databases, no JavaScript.  
- Example `index.html`:  
  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <title>Onion Store</title>
  </head>
  <body>
      <h1>Welcome to My Onion Shop</h1>
      <p>Products:</p>
      <ul>
          <li>Product 1 - 0.01 BTC</li>
          <li>Product 2 - 0.02 BTC</li>
      </ul>
      <p>Contact: yourstore@example.onion (PGP Encrypted)</p>
  </body>
  </html>
  ```  

### **Option B: Dynamic Site (Flask + SQLite)**  
- **Install Python & Flask:**  
  ```bash
  sudo apt install python3 python3-pip  
  pip3 install flask  
  ```  
- **Basic Flask App (`app.py`):**  
  ```python
  from flask import Flask, render_template
  app = Flask(__name__)

  @app.route('/')
  def home():
      products = [{"name": "Product 1", "price": "0.01 BTC"},
                 {"name": "Product 2", "price": "0.02 BTC"}]
      return render_template('index.html', products=products)

  if __name__ == '__main__':
      app.run(port=8080)
  ```  
- Run with:  
  ```bash
  torsocks python3 app.py
  ```  

---

# **Step 4: Accept Payments (Bitcoin/Monero Only)**  
### **4.1 Bitcoin (BTCPay Server Self-Hosted)**  
- Install BTCPay Server ([guide](https://docs.btcpayserver.org/))  
- **Never use Coinbase, Binance, etc.** (KYC risks).  

### **4.2 Monero (XMR) – Best for Privacy**  
- Use **Monero Wallet RPC** ([setup guide](https://getmonero.org/resources/user-guides/))  
- Generate a new wallet:  
  ```bash
  monero-wallet-cli --generate-new-wallet my_store_wallet
  ```  

---

# **Step 5: Security & Anonymity Checklist**  
✅ **No Logs** (Disable Nginx/Apache logging)  
✅ **Firewall Rules** (Block all non-Tor traffic)  
✅ **No JavaScript** (Prevents exploits)  
✅ **PGP Encryption** (For customer emails)  
✅ **Never Reuse Addresses** (Monero/Bitcoin)  
✅ **Regular Updates** (`sudo apt update && sudo apt upgrade`)  

---

# **Final Notes**  
- **Never log customer data.**  
- **Use PGP for all communications.**  
- **Test thoroughly before launch.**  
- **Assume law enforcement is watching.**  

---

# **Example Onion Store URL**  
`http://yourstorexyz.onion`  

This setup minimizes risk while allowing a functional e-commerce presence. **Proceed with caution.** 🚨