# Order - 咖啡店点单系统初始化方案

## 项目概述

| 维度 | 决策 |
|------|------|
| **项目名称** | `order` |
| **仓库位置** | `/home/sang/src/github.com/gitsang/order` |
| **仓库结构** | Monorepo，独立仓库 |
| **前端（用户端）** | Svelte + SvelteKit |
| **前端（管理后台）** | Svelte + SvelteKit |
| **后端** | Go + go-chi + protobuf + grpc-gateway + 自定义 protoc 插件 + GORM |
| **数据库** | PostgreSQL |
| **认证** | JWT |
| **定位** | MVP 原型 |

## MVP 核心功能

1. **用户点单流程** - 浏览菜单、加入购物车、下单
2. **支付集成** - 微信/支付宝支付
3. **用户系统** - 登录注册、会员积分
4. **后台管理** - 商品管理、订单管理、数据统计
5. **店员端** - 接单、出单状态更新

---

## 目录结构

```
order/
├── api/                           # Protobuf API 定义
│   └── order/
│       └── v1/
│           ├── order.proto        # 服务定义
│           └── *.pb.go            # 生成的代码
│
├── web/                           # Svelte 前端（用户端 + 管理后台）
│   ├── src/
│   │   ├── routes/
│   │   │   ├── (customer)/        # 用户端路由组
│   │   │   │   ├── +layout.svelte
│   │   │   │   ├── +page.svelte   # 首页/菜单
│   │   │   │   ├── cart/          # 购物车
│   │   │   │   └── order/         # 订单
│   │   │   └── (admin)/           # 管理后台路由组
│   │   │       ├── +layout.svelte
│   │   │       ├── +page.svelte   # Dashboard
│   │   │       ├── products/      # 商品管理
│   │   │       └── orders/        # 订单管理
│   │   ├── lib/
│   │   │   ├── components/        # 通用组件 (shadcn-svelte)
│   │   │   ├── stores/            # 状态管理
│   │   │   ├── utils/             # 工具函数
│   │   │   └── types/             # TypeScript 类型
│   │   └── app.html
│   ├── static/
│   ├── package.json
│   ├── svelte.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── cmd/                           # Go 入口
│   └── server/
│       └── main.go                # 主服务入口
│
├── internal/                      # 私有代码（不可被外部导入）
│   ├── config/                    # 配置管理
│   │   └── config.go
│   ├── handler/                   # gRPC/HTTP handlers
│   │   └── order.go
│   ├── service/                   # 业务逻辑层
│   │   └── order.go
│   ├── repo/                      # 数据访问层
│   │   └── order.go
│   └── model/                     # 领域模型
│       └── order.go
│
├── pkg/                           # 公共库（可被外部导入）
│   ├── auth/                      # JWT 认证
│   │   └── jwt.go
│   ├── database/                  # 数据库连接
│   │   └── postgres.go
│   └── middleware/                # Chi 中间件
│       └── cors.go
│
├── tools/                         # 工具和插件
│   ├── proto.sh                   # Protobuf 编译脚本
│   └── protoc-gen-custom/         # 自定义 protoc 插件
│       └── main.go
│
├── migrations/                    # 数据库迁移
│   ├── 000001_init_schema.up.sql
│   └── 000001_init_schema.down.sql
│
├── deploy/                        # 部署配置
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── k8s/                       # Kubernetes (可选)
│
├── docs/                          # 文档
│   └── api/                       # API 文档
│
├── Makefile                       # 统一构建命令
├── .gitignore
├── go.mod
├── go.sum
└── README.md
```

---

## 工程化配置

### 开发工具链

| 项目 | 工具 | 说明 |
|------|------|------|
| **前端构建** | Vite + SvelteKit | 快速 HMR，SSR 支持 |
| **前端包管理** | pnpm | 快速、节省磁盘空间 |
| **后端包管理** | Go Modules | 官方依赖管理 |
| **前端规范** | ESLint + Prettier | 代码格式化 |
| **后端规范** | golangci-lint | Go 代码检查 |
| **API 定义** | protobuf + grpc-gateway | IDL 定义，自动生成 HTTP 映射 |
| **数据库迁移** | golang-migrate | 版本化迁移 |
| **构建工具** | Makefile | 统一命令入口 |
| **容器化** | Docker + docker-compose | 本地开发环境 |

### Makefile 命令设计

```makefile
# ==================== 初始化 ====================
init:                   # 初始化项目
  go mod init
  pnpm install
  docker-compose up -d postgres

# ==================== 代码生成 ====================
proto:                  # 编译 protobuf
  protoc --go_out=. --go-grpc_out=. api/order/v1/*.proto
  protoc --grpc-gateway_out=. api/order/v1/*.proto

# ==================== 开发 ====================
dev:                    # 启动全部开发环境
  make -j2 dev-server dev-web

dev-server:             # 启动后端 (hot-reload)
  air -c .air.toml

dev-web:                # 启动前端
  cd app/web && pnpm dev

dev-admin:              # 启动管理后台
  cd app/admin && pnpm dev

# ==================== 构建 ====================
build:                  # 构建全部
  make build-server build-web build-admin

build-server:           # 构建后端
  go build -o bin/server cmd/server/main.go

build-web:              # 构建前端
  cd app/web && pnpm build

build-admin:            # 构建管理后台
  cd app/admin && pnpm build

# ==================== 数据库 ====================
migrate-up:             # 运行迁移
  migrate -path migrations -database "$(DB_URL)" up

migrate-down:           # 回滚迁移
  migrate -path migrations -database "$(DB_URL)" down 1

migrate-create:         # 创建新迁移
  migrate create -ext sql -dir migrations $(NAME)

# ==================== 检查 ====================
lint:                   # 代码检查
  golangci-lint run
  cd app/web && pnpm lint
  cd app/admin && pnpm lint

test:                   # 运行测试
  go test ./...
  cd app/web && pnpm test
  cd app/admin && pnpm test
```

---

## 初始依赖

### 后端 (go.mod)

```go
module github.com/gitsang/order

go 1.22

require (
    // HTTP 路由
    github.com/go-chi/chi/v5 v5.0.12
    github.com/go-chi/cors v1.2.1
    
    // gRPC
    google.golang.org/grpc v1.62.1
    google.golang.org/protobuf v1.33.0
    github.com/grpc-ecosystem/grpc-gateway/v2 v2.19.1
    
    // JWT
    github.com/golang-jwt/jwt/v5 v5.2.0
    
    // PostgreSQL (GORM)
    gorm.io/gorm v1.25.7
    gorm.io/driver/postgres v1.5.6
    
    // 配置
    github.com/spf13/viper v1.18.2
    
    // 日志
    go.uber.org/zap v1.27.0
    
    // 工具
    github.com/google/uuid v1.6.0
    golang.org/x/crypto v0.19.0  // bcrypt
)
```

### 前端 (package.json)

```json
{
  "name": "order-web",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "prettier --check . && eslint .",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "@sveltejs/adapter-auto": "^3.0.0",
    "@sveltejs/kit": "^2.0.0",
    "@sveltejs/vite-plugin-svelte": "^3.0.0",
    "svelte": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "prettier": "^3.2.0",
    "prettier-plugin-svelte": "^3.1.0",
    "eslint": "^8.56.0",
    "eslint-plugin-svelte": "^2.35.0"
  },
  "dependencies": {
    "bits-ui": "^0.11.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "tailwind-variants": "^0.1.20"
  },
  "type": "module"
}
```

> **UI 框架**: 使用 shadcn-svelte，通过 preset 初始化（preset id 待提供）

---

## 数据库 Schema 预览

### 核心表

```sql
-- 用户表
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone       VARCHAR(20) UNIQUE,
    nickname    VARCHAR(50),
    avatar_url  TEXT,
    points      INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 商品分类表
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 商品表
CREATE TABLE products (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id INTEGER REFERENCES categories(id),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    price       DECIMAL(10,2) NOT NULL,
    image_url   TEXT,
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 订单表
CREATE TABLE orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no        VARCHAR(32) UNIQUE NOT NULL,
    user_id         UUID REFERENCES users(id),
    total_amount    DECIMAL(10,2) NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending/paid/preparing/completed/cancelled
    payment_method  VARCHAR(20),
    payment_time    TIMESTAMPTZ,
    remark          TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 订单项表
CREATE TABLE order_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id    UUID REFERENCES orders(id),
    product_id  UUID REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Protobuf 定义预览

```protobuf
// api/order/v1/order.proto
syntax = "proto3";

package order.v1;

option go_package = "github.com/gitsang/order/api/order/v1";

import "google/api/annotations.proto";

// ==================== 商品服务 ====================
service ProductService {
    rpc ListProducts(ListProductsRequest) returns (ListProductsResponse) {
        option (google.api.http) = {
            get: "/api/v1/products"
        };
    }
    
    rpc GetProduct(GetProductRequest) returns (Product) {
        option (google.api.http) = {
            get: "/api/v1/products/{id}"
        };
    }
}

message Product {
    string id = 1;
    string name = 2;
    string description = 3;
    double price = 4;
    string image_url = 5;
    int32 category_id = 6;
}

message ListProductsRequest {
    int32 category_id = 1;
    int32 page = 2;
    int32 page_size = 3;
}

message ListProductsResponse {
    repeated Product products = 1;
    int32 total = 2;
}

message GetProductRequest {
    string id = 1;
}

// ==================== 订单服务 ====================
service OrderService {
    rpc CreateOrder(CreateOrderRequest) returns (Order) {
        option (google.api.http) = {
            post: "/api/v1/orders"
            body: "*"
        };
    }
    
    rpc GetOrder(GetOrderRequest) returns (Order) {
        option (google.api.http) = {
            get: "/api/v1/orders/{id}"
        };
    }
    
    rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse) {
        option (google.api.http) = {
            get: "/api/v1/orders"
        };
    }
}

message Order {
    string id = 1;
    string order_no = 2;
    string user_id = 3;
    double total_amount = 4;
    string status = 5;
    repeated OrderItem items = 6;
    string remark = 7;
    string created_at = 8;
}

message OrderItem {
    string product_id = 1;
    string product_name = 2;
    int32 quantity = 3;
    double price = 4;
}

message CreateOrderRequest {
    repeated CreateOrderItem items = 1;
    string remark = 2;
}

message CreateOrderItem {
    string product_id = 1;
    int32 quantity = 2;
}

message GetOrderRequest {
    string id = 1;
}

message ListOrdersRequest {
    string status = 1;
    int32 page = 2;
    int32 page_size = 3;
}

message ListOrdersResponse {
    repeated Order orders = 1;
    int32 total = 2;
}
```

---

## 开发环境要求

### 必需工具

```bash
# Go
go version  # >= 1.22

# Node.js
node -v     # >= 18
pnpm -v     # >= 8

# Protobuf
protoc --version           # >= 3.21
protoc-gen-go             # go install google.golang.org/protobuf/cmd/protoc-gen-go
protoc-gen-go-grpc        # go install google.golang.org/grpc/cmd/protoc-gen-go-grpc
protoc-gen-grpc-gateway   # go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway

# 数据库
psql --version            # PostgreSQL >= 14

# 开发工具 (推荐)
air                       # Go hot-reload
golangci-lint             # Go linter
```

### Docker 本地开发

```yaml
# deploy/docker/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: order
      POSTGRES_PASSWORD: order123
      POSTGRES_DB: order
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 实施步骤

### Phase 1: 项目初始化 (Day 1)

- [ ] 创建 Git 仓库
- [ ] 初始化目录结构
- [ ] 配置 Go modules
- [ ] 配置 pnpm workspace
- [ ] 配置 Makefile
- [ ] 配置 .gitignore
- [ ] 配置 docker-compose
- [ ] 编写 README.md

### Phase 2: 后端基础 (Day 2-3)

- [ ] 定义 protobuf
- [ ] 配置 protoc 编译
- [ ] 实现 config 加载
- [ ] 实现数据库连接
- [ ] 实现 JWT 认证
- [ ] 实现 Chi 路由 + 中间件
- [ ] 实现基础 CRUD handler

### Phase 3: 前端基础 (Day 3-4)

- [ ] 初始化 SvelteKit 项目
- [ ] 配置 API 代理
- [ ] 实现基础布局
- [ ] 实现路由结构
- [ ] 实现 API 调用层
- [ ] 实现状态管理

### Phase 4: 核心功能 (Day 5-7)

- [ ] 商品列表/详情
- [ ] 购物车
- [ ] 下单流程
- [ ] 订单列表
- [ ] 管理后台基础

---

## 后续扩展

- [ ] 微信小程序 (uni-app)
- [ ] 支付宝小程序
- [ ] 支付集成
- [ ] 消息推送
- [ ] 数据统计
- [ ] 店员端 App
