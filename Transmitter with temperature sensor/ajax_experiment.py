import machine



# ************************
# Configure the ESP32 wifi
# as STAtion mode.
import network

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-WeatherStation', password='your_password')
print('network config:', ap.ifconfig())

# ************************
# Configure the socket connection
# over TCP/IP
import socket

# AF_INET - use Internet Protocol v4 addresses
# SOCK_STREAM means that it is a TCP socket.
# SOCK_DGRAM means that it is a UDP socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80)) # specifies that the socket is reachable by any address the machine happens to have
s.listen(5)     # max of 5 socket connections

# ************************
# Function for creating the
# web page to be displayed
def web_page():
    html_page = """
<!DOCTYPE html>  
 <html>  
  <head>  
  <meta name='viewport' content='width=device-width, initial-scale=1.0'/>  
  <script>   
   var ajaxRequest = new XMLHttpRequest();  
   
   function ajaxLoad(ajaxURL)  
   {  
    ajaxRequest.open('GET',ajaxURL,true);  
    ajaxRequest.onreadystatechange = function()  
    {  
     if(ajaxRequest.readyState == 4 && ajaxRequest.status==200)  
     {  
      var ajaxResult = ajaxRequest.responseText;  
      var tmpArray = ajaxResult.split("|");  
      document.getElementById('temp').innerHTML = tmpArray[0];  
      document.getElementById('humi').innerHTML = tmpArray[1];  
     }  
    }  
    ajaxRequest.send();  
   }  
     
   function updateDHT()   
   {   
     ajaxLoad('getDHT');   
   }  
     
   setInterval(updateDHT, 3000);  
    
  </script>  
    
    
  <title>ESP32 Weather Station</title>  
  </head>  
    
  <body>  
   <center>  
   <div id='main'>  
    <h1>MicroPython Weather Station</h1>  
    <h4>Web server on ESP32 | DHT values auto updates using AJAX.</h4>  
    <div id='content'>   
     <p>Temperature: <strong><span id='temp'>--.-</span> &deg;C</strong></p>  
     <p>Humidity: <strong><span id='humi'>--.-</span> % </strong></p>  
    </div>  
   </div>  
   </center>  
  </body>  
 </html>
"""
    return html_page

while True:
    
    # Socket accept() 
    conn, addr = s.accept()
    print("Got connection from %s" % str(addr))
    
    # Socket receive()
    request=conn.recv(1024)
    print("")
    print("Content %s" % str(request))

    # Socket send()
    request = str(request)
    update = request.find('/getDHT')
    if update == 6:
        t = str(25)
        h = str(20)
        response = str(t) + "|"+ str(h)
        led.value(not led.value())
    else:
        response = web_page()
        
    # Create a socket reply
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    
    # Socket close()
    conn.close()