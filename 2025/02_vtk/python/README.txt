
Для просмотра анимации:
1. Откройте ParaView
2. File -> Open -> выберите animation.pvd
3. Нажмите Apply

Доступные поля:
- Velocity: векторное поле вибрации
- Pressure: скалярное поле давления
- Speed: модуль скорости (для окрашивания)

Для видимой вибрации в ParaView:
1. Добавьте фильтр "Warp By Vector"
2. Выберите Velocity как Vector
3. Увеличьте Scale Factor (10-50)
