├── src
│   ├── api                           # Thư mục chứa source code chính
│   │   ├── axiosInstance.js          # Cấu hình Axios (nếu dùng Axios)
│   │   └── user.js                   # API cho người dùng
│   │   └── auth.js                   # API xác thực
│   ├── assets                        # Thư mục chứa assets (hình ảnh, icon, fonts, v.v.)
│   │   ├── images
│   │   ├── icons
│   │   └── fonts
│   ├── components
│   │   ├── ui                        # Các component dùng chung
│   │   │   └── ...                   # Các component UI chung (Button, Modal, ...)
│   │   └── layout                    # Layout (Header, Footer, Sidebar, ...)
│   ├── composables                   # Custom hooks (Vue 3 Composition API)
│   │   ├── useAuth.js
│   │   └── useForm.js
│   ├── directives                    # Custom directives (v-click-outside, v-focus, ...)
│   ├── layouts                       # Layouts (Admin, Auth, Main, ...)
│   │   ├── DefaultLayout.vue
│   │   └── AuthLayout.vue
│   ├── router
│   │   ├── index.js                  # Cấu hình Vue Router
│   │   ├── routes.js                 # Router chính
│   │   ├── auth.js                   # Phân tách các routes
│   │   └── guards.js                 # Navigation guards (nếu cần)
│   ├── store
│   │   ├── index.js                  # Vuex/Pinia (Quản lý state)
│   │   ├── auth.js                   # Store chung
│   │   └── user.js                   # Store module: Auth
│   │                                  # Store module: User
│   ├── styles
│   │   ├── main.css                  # Chứa file CSS/SCSS
│   │   ├── variables.scss            # CSS chính
│   │   ├── mixins.scss               # Biến CSS
│   │   └── tailwind.css              # Mixins SCSS
│   │                                 # Nếu dùng TailwindCSS
│   └── views                         # Các page chính
│       ├── Home.vue
│       ├── Login.vue
│       ├── Register.vue
│       └── Profile.vue
│       └── ...
├── App.vue                           # Component gốc
├── main.js                           # File khởi tạo Vue
├── i18n.js                           # Đa ngôn ngữ (nếu dùng Vue I18n)
└── shims-vue.d.ts                    # Khai báo kiểu cho tệp .vue
    └── ...
├── public
│   ├── index.html                    # Thư mục chứa các file tĩnh (favicon, manifest, ...)
│   └── favicon.ico                   # Template HTML chính
│   └── ...
├── tests
│   ├── unit                          # Chứa các file test (Unit Test, E2E Test)
│   │   └── ...                       # Unit Test (Jest, Vitest)
│   └── e2e                           # End-to-End Test (Cypress, Playwright)
│       └── ...
├── .vscode                           # Cấu hình VSCode (Extensions, Settings, ...)
├── .gitignore                        # File cấu hình Git Ignore
├── .editorconfig                     # Các tệp format code
├── package.json                      # File quản lý dependencies
├── vite.config.js                    # Cấu hình Vite (hoặc vue.config.js nếu dùng Vue CLI)
├── tailwind.config.js                # Cấu hình TailwindCSS (nếu dùng)
├── tsconfig.json                     # Cấu hình TypeScript (nếu dùng TypeScript)
└── README.md                         # File mô tả dự án