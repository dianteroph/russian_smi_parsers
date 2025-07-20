# Парсинг российских СМИ: 
### На примере Meduza, RussiaToday, Коммерсант

<img width="1500" height="700" alt="wc_parsing3" src="https://github.com/user-attachments/assets/e5f4e97a-166a-4a70-8f85-81a668390da0" />
Как основные инструменты использовались классические библиотеки в Python: **requests, BeautifulSoup, Selenium**.
Репозиторий содержит три полноценных парсера, которые хранятся в скриптах: 
- `meduza_parsing` - c классом `MeduzaParser`
- `russia_today_parsing` - с классом `RussiaTodayParser`
- `kommersant_parsing` - с классом `Kommersantparser`

А также csv файл с примером собранных статей по запросу 'выборы в сша' c сайта Медузы. 
