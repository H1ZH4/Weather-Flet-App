import flet as ft
import requests
import json
from datetime import datetime
import os
import random

API_KEY = "add-your-api-token"
BASE_URL = "http://api.openweathermap.org/data/2.5"

WEATHER_IMAGES = {
    "clear": "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=1000",
    "clouds": "  https://images.unsplash.com/photo-1569428034239-f9565e32e224?w=1000",
    "rain": "  https://images.unsplash.com/photo-1433863448220-78aaa064ff47?w=1000",
    "snow": "  https://images.unsplash.com/photo-1542603188-5e5c75d3bf2e?w=1000",
    "thunderstorm": "  https://images.unsplash.com/photo-1594006558723-278ae6c070db?w=1000",
    "drizzle": "  https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1000",
    "mist": "  https://images.unsplash.com/photo-1504253163759-c23fccaebb55?w=1000",
    "default": "  https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=1000"
}

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Weather App"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        
        self.favorite_cities = self.load_favorites()
        
        self.create_ui()
        
        self.get_weather_by_city("Tehran")
    
    def create_ui(self):
        self.search_field = ft.TextField(
            label="نام شهر را وارد کنید",
            on_submit=self.search_city,
            expand=True,
            border_color=ft.Colors.BLUE_700,
            focused_border_color=ft.Colors.BLUE_900
        )
        
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            on_click=self.search_city,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            tooltip="جستجوی شهر"
        )
        
        self.favorite_button = ft.IconButton(
            icon=ft.Icons.FAVORITE_BORDER,
            on_click=self.toggle_favorite,
            tooltip="افزودن به علاقه‌مندی‌ها",
            icon_color=ft.Colors.RED
        )
        
        self.city_name = ft.Text(size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.current_temp = ft.Text(size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.weather_desc = ft.Text(size=18, color=ft.Colors.WHITE)
        self.weather_icon = ft.Image(src="", width=100, height=100)
        
        self.feels_like = ft.Text(color=ft.Colors.WHITE)
        self.humidity = ft.Text(color=ft.Colors.WHITE)
        self.wind_speed = ft.Text(color=ft.Colors.WHITE)
        self.pressure = ft.Text(color=ft.Colors.WHITE)
        self.visibility = ft.Text(color=ft.Colors.WHITE)
        
        self.forecast_container = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
        
        self.favorites_list = ft.Column()
        self.update_favorites_list()
        
        self.background_image = ft.Image(
            src=WEATHER_IMAGES["default"],
            width=self.page.width,
            height=self.page.height,
            fit=ft.ImageFit.COVER,
            opacity=0.3
        )
        
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.search_field,
                            self.search_button,
                            self.favorite_button
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    self.city_name,
                                    self.current_temp,
                                    self.weather_desc
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            self.weather_icon
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    self.feels_like,
                                    self.humidity,
                                    self.wind_speed
                                ]
                            ),
                            ft.Column(
                                controls=[
                                    self.pressure,
                                    self.visibility,
                                    ft.Container()
                                ]
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Text("پیش‌بینی 5 روز آینده", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    self.forecast_container,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Text("شهرهای مورد علاقه", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    self.favorites_list
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900),
            width=min(800, self.page.width - 40),
        )
        
        self.page.add(
            ft.Stack(
                controls=[
                    self.background_image,
                    ft.Column(
                        controls=[
                            ft.Text("برنامه آب و هوا", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            self.main_container
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO
                    )
                ],
                expand=True
            )
        )
    
    def load_favorites(self):
        if os.path.exists("favorites.json"):
            with open("favorites.json", "r") as f:
                return json.load(f)
        return []
    
    def save_favorites(self):
        with open("favorites.json", "w") as f:
            json.dump(self.favorite_cities, f)
    
    def update_favorites_list(self):
        self.favorites_list.controls.clear()
        for city in self.favorite_cities:
            self.favorites_list.controls.append(
                ft.ListTile(
                    title=ft.Text(city, color=ft.Colors.WHITE),
                    on_click=lambda e, c=city: self.get_weather_by_city(c),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, c=city: self.remove_favorite(c),
                        icon_color=ft.Colors.RED
                    )
                )
            )
        self.page.update()
    
    def toggle_favorite(self, e):
        current_city = self.city_name.value
        if current_city:
            if current_city in self.favorite_cities:
                self.favorite_cities.remove(current_city)
                self.favorite_button.icon = ft.Icons.FAVORITE_BORDER
            else:
                self.favorite_cities.append(current_city)
                self.favorite_button.icon = ft.Icons.FAVORITE
            self.save_favorites()
            self.update_favorites_list()
            self.page.update()
    
    def remove_favorite(self, city):
        if city in self.favorite_cities:
            self.favorite_cities.remove(city)
            self.save_favorites()
            self.update_favorites_list()
    
    def search_city(self, e):
        city = self.search_field.value.strip()
        if city:
            self.get_weather_by_city(city)
    
    def get_weather_by_city(self, city):
        current_weather_url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric&lang=fa"
        
        try:
            response = requests.get(current_weather_url)
            data = response.json()
            
            if response.status_code == 200:
                self.display_current_weather(data)
                
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]
                self.get_forecast(lat, lon)
                
                if city in self.favorite_cities:
                    self.favorite_button.icon = ft.Icons.FAVORITE
                else:
                    self.favorite_button.icon = ft.Icons.FAVORITE_BORDER
                    
                self.page.update()
            else:
                self.show_error(f"شهر '{city}' یافت نشد.")
                
        except Exception as ex:
            self.show_error(f"خطا در دریافت اطلاعات: {str(ex)}")
    
    def get_forecast(self, lat, lon):
        forecast_url = f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=fa"
        
        try:
            response = requests.get(forecast_url)
            data = response.json()
            
            if response.status_code == 200:
                self.display_forecast(data)
            else:
                self.show_error("خطا در دریافت پیش‌بینی آب و هوا")
                
        except Exception as ex:
            self.show_error(f"خطا در دریافت پیش‌بینی: {str(ex)}")
    
    def display_current_weather(self, data):
        self.city_name.value = data["name"] + ", " + data["sys"]["country"]
        self.current_temp.value = f"{round(data['main']['temp'])}°C"
        self.weather_desc.value = data["weather"][0]["description"].capitalize()
        
        icon_code = data["weather"][0]["icon"]
        self.weather_icon.src = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        self.feels_like.value = f"دمای احساسی: {round(data['main']['feels_like'])}°C"
        self.humidity.value = f"رطوبت: {data['main']['humidity']}%"
        self.wind_speed.value = f"سرعت باد: {data['wind']['speed']} m/s"
        self.pressure.value = f"فشار: {data['main']['pressure']} hPa"
        
        visibility_km = data.get("visibility", 0) / 1000
        self.visibility.value = f"دید: {visibility_km} km"
        
        weather_condition = data["weather"][0]["main"].lower()
        if weather_condition in WEATHER_IMAGES:
            self.background_image.src = WEATHER_IMAGES[weather_condition]
        else:
            self.background_image.src = WEATHER_IMAGES["default"]
    
    def display_forecast(self, data):
        self.forecast_container.controls.clear()
        
        daily_forecasts = {}
        for forecast in data["list"]:
            date = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(forecast)
        
        for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:5]):
            day_forecast = None
            for forecast in forecasts:
                forecast_time = datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")
                if forecast_time == "12:00":
                    day_forecast = forecast
                    break
            
            if not day_forecast:
                day_forecast = forecasts[0]
            
            forecast_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(datetime.strptime(date, "%Y-%m-%d").strftime("%a %d %b"), color=ft.Colors.WHITE),
                        ft.Image(
                            src=f"http://openweathermap.org/img/wn/{day_forecast['weather'][0]['icon']}.png",
                            width=50,
                            height=50
                        ),
                        ft.Text(f"{round(day_forecast['main']['temp_max'])}°C", color=ft.Colors.WHITE),
                        ft.Text(f"{round(day_forecast['main']['temp_min'])}°C", size=12, color=ft.Colors.WHITE),
                        ft.Text(day_forecast["weather"][0]["description"].capitalize(), size=12, color=ft.Colors.WHITE)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_700),
                width=120
            )
            
            self.forecast_container.controls.append(forecast_card)
    
    def show_error(self, message):
        self.city_name.value = ""
        self.current_temp.value = ""
        self.weather_desc.value = ""
        self.weather_icon.src = ""
        self.feels_like.value = ""
        self.humidity.value = ""
        self.wind_speed.value = ""
        self.pressure.value = ""
        self.visibility.value = ""
        self.forecast_container.controls.clear()
        
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    page.window.width = 900
    page.window.height = 800
    page.window.resizable = True
    page.title = "Weather App"
    WeatherApp(page)

if __name__ == "__main__":
    ft.app(target=main)
