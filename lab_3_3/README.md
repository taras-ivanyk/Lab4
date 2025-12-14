## 👤 User
| Method        | Endpoint           | Description                      |
| ------------- | ------------------ | -------------------------------- |
| `GET`         | `/api/users/`      | (R) Get list of all users        |
| `POST`        | `/api/users/`      | (C) Create (register) a new user |
| `GET`         | `/api/users/<pk>/` | (R) Get a user by ID             |
| `PUT / PATCH` | `/api/users/<pk>/` | (U) Update a user                |
| `DELETE`      | `/api/users/<pk>/` | (D) Delete a user                |

## 🏋️‍♀️ Activity
| Method        | Endpoint                | Description                            |
| ------------- | ----------------------- | -------------------------------------- |
| `GET`         | `/api/activities/`      | (R) Get all activities                 |
| `POST`        | `/api/activities/`      | (C) Create a new activity              |
| `GET`         | `/api/activities/<pk>/` | (R) Get one activity                   |
| `PUT / PATCH` | `/api/activities/<pk>/` | (U) Update an activity (only your own) |
| `DELETE`      | `/api/activities/<pk>/` | (D) Delete an activity (only your own) |

## 👥 Profile
| Method        | Endpoint              | Description                               |
| ------------- | --------------------- | ----------------------------------------- |
| `GET`         | `/api/profiles/`      | (R) Get all profiles                      |
| `POST`        | `/api/profiles/`      | (C) Create a profile (for `request.user`) |
| `GET`         | `/api/profiles/<pk>/` | (R) Get a profile (pk = user_id)          |
| `PUT / PATCH` | `/api/profiles/<pk>/` | (U) Update a profile (only your own)      |
| `DELETE`      | `/api/profiles/<pk>/` | (D) Delete a profile (only your own)      |

## 💬 Comment
| Method        | Endpoint              | Description                 |
| ------------- | --------------------- | --------------------------- |
| `GET`         | `/api/comments/`      | (R) Get all comments        |
| `POST`        | `/api/comments/`      | (C) Create a new comment    |
| `GET`         | `/api/comments/<pk>/` | (R) Get one comment         |
| `PUT / PATCH` | `/api/comments/<pk>/` | (U) Update your own comment |
| `DELETE`      | `/api/comments/<pk>/` | (D) Delete your own comment |

## ❤️ Kudos (Likes)
| Method   | Endpoint           | Description              |
| -------- | ------------------ | ------------------------ |
| `GET`    | `/api/kudos/`      | (R) Get all likes        |
| `POST`   | `/api/kudos/`      | (C) Create a like        |
| `GET`    | `/api/kudos/<pk>/` | (R) Get one like         |
| `DELETE` | `/api/kudos/<pk>/` | (D) Delete your own like |

## 👣 Follower
| Method   | Endpoint          | Description                                       |
| -------- | ----------------- | ------------------------------------------------- |
| `GET`    | `/api/followers/` | (R) Get all follows                               |
| `POST`   | `/api/followers/` | (C) Follow another user (`followee` in JSON body) |
| `DELETE` | `/api/followers/` | (D) Unfollow (`followee_id` in JSON body)         |

## 📍 Activity Point
| Method        | Endpoint                     | Description                                 |
| ------------- | ---------------------------- | ------------------------------------------- |
| `GET`         | `/api/activity-points/`      | (R) Get all activity points                 |
| `POST`        | `/api/activity-points/`      | (C) Create a point (for your activity only) |
| `GET`         | `/api/activity-points/<pk>/` | (R) Get one point                           |
| `PUT / PATCH` | `/api/activity-points/<pk>/` | (U) Update a point (your activity only)     |
| `DELETE`      | `/api/activity-points/<pk>/` | (D) Delete a point (your activity only)     |

## 📊 User Monthly Stats
| Method | Endpoint           | Description                                   |
| ------ | ------------------ | --------------------------------------------- |
| `GET`  | `/api/user-stats/` | (R) Get all user statistics (C/U/D forbidden) |

## 📈 Reports (Statistics)
| Method | Endpoint                     | Description                             |
| ------ | ---------------------------- | --------------------------------------- |
| `GET`  | `/api/reports/global-stats/` | (R) Get a global statistics JSON report |


### Для взаємодії з проєктом друга потрібно:
1) Запустити його сервер (порт 8001)
2) http://127.0.0.1:8001/clients/ - додати клієнта
3) http://127.0.0.1:8000/ui/external-activities/ - через мій проєкт побачимо спадний список де можемо видалити клієнта і побачити дані про нього
4) http://127.0.0.1:8000/ui/comments/ - для роботи з даними у шаблонах