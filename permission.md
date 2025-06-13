# **Managing Permissions on Whonix Workstation**  
To properly run your e-commerce site on Whonix Workstation, you'll need to configure permissions for:  
1. Application files (`/var/www/`)  
2. Network ports (8080)  
3. Monero wallet  
4. Service execution  

Here's how to set up permissions securely:

---

## **1. Directory Ownership & Permissions**  
### Create dedicated user for your e-commerce app:  
```bash  
sudo adduser --system --group ecom-user  
```  

### Assign ownership of application directory:  
```bash  
sudo mkdir -p /var/www/ecom-store  
sudo chown -R ecom-user:ecom-user /var/www/ecom-store  
```  

### Set secure permissions:  
```bash  
sudo chmod 750 /var/www/ecom-store  # Owner: RWX, Group: RX  
find /var/www/ecom-store -type d -exec chmod 750 {} \;  
find /var/www/ecom-store -type f -exec chmod 640 {} \;  
```

---

## **2. Port Access (8080)**  
### Allow non-root user to bind to port 8080:  
```bash  
sudo apt install authbind  
sudo touch /etc/authbind/byport/8080  
sudo chown ecom-user /etc/authbind/byport/8080  
sudo chmod 500 /etc/authbind/byport/8080  
```  

### Update your Flask command:  
```bash  
authbind --deep torsocks python3 /var/www/ecom-store/app.py  
```

---

## **3. Monero Wallet Permissions**  
### Create secure wallet directory:  
```bash  
sudo mkdir /etc/monero-wallet  
sudo chown ecom-user:ecom-user /etc/monero-wallet  
sudo chmod 700 /etc/monero-wallet  # Only owner can access  
```  

### Generate wallet as application user:  
```bash  
sudo -u ecom-user monero-wallet-cli --generate-new-wallet /etc/monero-wallet/store_wallet  
```

---

## **4. Service Management (Systemd)**  
### Create service file:  
```bash  
sudo nano /etc/systemd/system/ecom-store.service  
```  

```ini  
[Unit]
Description=Onion E-Commerce Service
After=network.target

[Service]
User=ecom-user
Group=ecom-user
WorkingDirectory=/var/www/ecom-store
ExecStart=/usr/bin/authbind --deep /usr/bin/torsocks /usr/bin/python3 /var/www/ecom-store/app.py
Restart=on-failure
RestartSec=5s

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=tmpfs
ReadWritePaths=/var/www/ecom-store /etc/monero-wallet

[Install]
WantedBy=multi-user.target
```  

### Enable the service:  
```bash  
sudo systemctl daemon-reload  
sudo systemctl enable ecom-store  
sudo systemctl start ecom-store  
```

---

## **5. Key Permission Commands Cheat Sheet**  
| **Task** | **Command** |  
|----------|-------------|  
| Change owner | `sudo chown user:group file` |  
| Change permissions | `sudo chmod permissions file` |  
| Run as specific user | `sudo -u username command` |  
| Check open ports | `sudo netstat -tulpn` |  
| Check service status | `sudo systemctl status ecom-store` |  
| View logs | `sudo journalctl -u ecom-store` |  

---

## **Troubleshooting Permission Issues**  
1. **"Permission denied" on port 8080**:  
   ```bash  
   sudo lsof -i :8080  # Check what's using the port  
   sudo kill <PID>     # Free the port if needed  
   ```  

2. **File access errors**:  
   ```bash  
   namei -l /path/to/file  # Check directory permissions chain  
   sudo -u ecom-user ls -l /path  # Test access as app user  
   ```  

3. **Wallet access problems**:  
   ```bash  
   sudo -u ecom-user monero-wallet-cli --wallet-file /etc/monero-wallet/store_wallet  
   ```  

---

## **Security Recommendations**  
1. **Principle of Least Privilege**:  
   - Never run services as root  
   - Use separate users for different services  

2. **Filesystem Protection**:  
   ```bash  
   sudo chattr +i /etc/monero-wallet/store_wallet  # Make wallet immutable  
   ```

3. **Regular Auditing**:  
   ```bash  
   sudo apt install auditd  
   sudo auditctl -w /etc/monero-wallet -p war -k monero_wallet  
   ```  

This configuration ensures your e-commerce site runs with minimal privileges while maintaining strict security boundaries.