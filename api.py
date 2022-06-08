from IPython.display import JSON
import pandas as pd

class Api():
    def __init__(self):
        self.api = JSON('https://ibnux.github.io/BMKG-importer/cuaca/wilayah.json')
        self.api_json = self.api.data

    def read(self):
        self.id= []
        self.propinsi= []
        self.kota=[]
        self.kecamatan=[]
        self.lat=[]
        self.lon=[]
        self.jamCuaca=[]
        self.kodeCuaca=[]
        self.cuaca=[]
        self.humidity=[]
        self.tempC=[]
        self.tempF=[]

        for x in self.api_json:
            if x['propinsi'] == 'JawaTengah' and x['kota'] == 'Kota Semarang':
                self.id.append(x['id'])
                self.propinsi.append(x['propinsi'])
                self.kota.append(x['kota'])
                self.kecamatan.append(x['kecamatan'])
                self.lat.append(x['lat'])
                self.lon.append(x['lon'])


        self.cuaca_api = JSON(f'https://ibnux.github.io/BMKG-importer/cuaca/{self.id[0]}.json')
        self.cuaca_json = self.cuaca_api.data

        # print(self.cuaca_json)

        for i in self.cuaca_json:
            if i['jamCuaca'] == '2022-06-06 00:00:00':
                self.jamCuaca.append(i['jamCuaca'])
                self.kodeCuaca.append(i['kodeCuaca'])
                self.cuaca.append(i['cuaca'])
                self.humidity.append(i['humidity'])
                self.tempC.append(i['tempC'])
                self.tempF.append(i['tempF'])

        self.df = pd.DataFrame({'id': self.id, 'propinsi': self.propinsi, 'kota': self.kota, 'kecamatan': self.kecamatan, 'lat':self.lat, 'lon': self.lon, 'jamCuaca': self.jamCuaca, 'kodeCuaca': self.kodeCuaca, 'cuaca': self.cuaca, 'humidity': self.humidity, 'tempC': self.tempC, 'tempF': self.tempF})
        return self.df

# model = Api()

# print(model.read())