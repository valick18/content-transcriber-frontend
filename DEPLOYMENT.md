# Deployment Guide: Vercel + Google Cloud

Ви хочете використовувати **Vercel**, і це чудовий вибір для **Фронтенду** (те, що бачить користувач).
Але **Бекенд** (Python, який качає відео і запускає штучний інтелект) занадто "важкий" для Vercel (там є ліміт 10 секунд на виконання, а відео обробляється довше).

Тому ми зробимо **Гібридну схему (Найкращий варіант)**:
1.  **Frontend** -> **Vercel** (Швидко, безкоштовно, гарний домен).
2.  **Backend** -> **Google Cloud Run** (Потужно, безкоштовний ліміт).

---

## Частина 1: Запуск Бекенду (Google Cloud Run)
Спочатку нам треба отримати посилання на працюючий сервер.

1.  **Встановіть Google Cloud SDK**:
    *   Завантажте інсталятор для Windows: [Google Cloud SDK Installer](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)
    *   Запустіть, натискайте "Next", "Next".
    *   В кінці відкриється термінал. Авторизуйтесь командою:
    ```bash
    gcloud auth login
    gcloud config set project contenttranscriber
    ```

2.  **Запустіть сервер у хмарі**:
    Відкрийте термінал у папці `backend` і виконайте:
    ```bash
    gcloud run deploy content-transcriber-api --source . --platform managed --region us-central1 --allow-unauthenticated --set-env-vars GROQ_API_KEY=ваш_ключ_groq
    ```

3.  **Скопіюйте URL**:
    Після успіху ви побачите щось типу: `https://content-transcriber-api-xyz.a.run.app`. **Збережіть це!**

---

## Частина 2: Запуск Фронтенду (Vercel)

1.  **Підготовка**:
    *   Зареєструйтесь на [vercel.com](https://vercel.com/).
    *   Встановіть Vercel CLI: `npm i -g vercel` (або просто перетягніть папку на сайті).

2.  **Деплой через термінал (Простий спосіб)**:
    *   Відкрийте термінал у папці `frontend`.
    *   Напишіть команду:
        ```bash
        vercel
        ```
    *   Погоджуйтесь з усім (Enter, Enter...).

3.  **Налаштування зв'язку**:
    *   Коли Vercel запитає "Want to modify settings?", скажіть **No** (або налаштуйте пізніше на сайті).
    *   Зайдіть у панель керування проектом на сайті Vercel.
    *   Перейдіть у **Settings** -> **Environment Variables**.
    *   Додайте нову змінну:
        *   **Key**: `VITE_API_URL`
        *   **Value**: Ваше посилання з Частини 1 (наприклад, `https://content-transcriber-api-xyz.a.run.app/api`) **(Важливо: додайте /api в кінці!)**
    *   Перезапустіть деплой (Redeploy) у вкладці Deployments.

**Готово!** Тепер у вас є швидкий сайт на Vercel, який звертається до потужного сервера Google.
