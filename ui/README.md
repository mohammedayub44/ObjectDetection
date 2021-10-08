# Crowd_Detection
Detecting large crowds with Videos and Camera feeds


## Running 

Start Flask Server:

`python service\app.py `

Post image Request (separate terminal):

`curl -X POST -F image=@"service/IMG_4.jpg" 'http://127.0.0.1:8080/predict'`

Data Returned:
```javascript
{ predict_time_ms":"760","predictions":{"count":"154.0","heatmap":"[[[[0.0928445 ]\n   [0.17732866]\n   [0.17231198]\n   ...\n   [0.02326113]\n   [0.04403671]\n   [0.04160059]]\n\n  [[0.06391969]\n   [0.1233318 ]\n   [0.1385351 ]\n   ...\n   [0.02002291]\n   [0.05446133]\n   [0.04844731]]\n\n  [[0.07501812]\n   [0.15517338]\n   [0.17023663]\n   ...\n   [0.08882342]\n   [0.05094147]\n   [0.05723583]]\n\n  ...\n\n  [[0.00743099]\n   [0.00695727]\n   [0.01426582]\n   ...\n   [0.00754658]\n   [0.00372858]\n   [0.00793823]]\n\n  [[0.01017613]\n   [0.00693572]\n   [0.01583   ]\n   ...\n   [0.00631961]\n   [0.01035042]\n   [0.01273389]]\n\n  [[0.00763646]\n   [0.00454946]\n   [0.0060876 ]\n   ...\n   [0.00599788]\n   [0.01181053]\n   [0.01865886]]]]"},"success":true,"total_time_ms":"775"}
