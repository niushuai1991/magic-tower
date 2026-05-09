# 第3关 BOSS事件链：初次遭遇 Zeno

> 来源：`MTower.java` 第3622-3744行（`eventMT`方法）+ 第13389-13398行（`displayConfigWindow`方法）

## 概述

当玩家在第3关（mapX=2, mapY=0）走到全局坐标 **(31, 9)**（局部坐标 (5, 9)）时，触发初次遭遇最终BOSS Zeno的事件链。这是一个**强制性的线性剧情事件**，包含像素变换动画、怪物召唤、传送和开篇剧情。

## 相关数据

### 存储位置

| 变量 | 存储位置 | 说明 |
|------|---------|------|
| event_3f | `obj_data[73][126]` | 3F事件状态，0=未触发 |
| event_counter | `obj_data[74][126]` | 子事件计数器 |
| flag3F | 实例变量 `int flag3F` | 控制擦除动画（0/1） |
| openningFlag | 实例变量 `boolean openningFlag` | 开篇模式（黑屏，不绘制地图） |
| mapFlagAll | 实例变量 `boolean mapFlagAll` | 全地图重绘标志 |

### 涉及的对象

| 对象ID | 名称 | crop1 | crop2 | HP | ATK | DEF | GOLD |
|--------|------|-------|-------|-----|-----|-----|------|
| 57 | Zeno（最终BOSS） | 121 | 122 | 8000 | 5000 | 1000 | 500 |
| 58 | Madoushi（魔法师） | 123 | 124 | 230 | 450 | 100 | 100 |

### 涉及的地图Tile

| Tile ID | 类型 | 说明 |
|---------|------|------|
| 116 | 楼梯(type=2) | jumpX=1, jumpY=66 → floor 51 |
| 117 | 楼梯(type=2) | jumpX=17, jumpY=8 → floor 2 局部(4,8) |

### 涉及的消息

| 消息ID | 英文内容 |
|--------|---------|
| 10 | Zeno: "Welcome to 'The Magic Tower'. You are the hundredth man..." |
| 222 | 勇者: "What?" |
| 223 | 勇者: "Hey!" |
| 266 | "------" |
| 2 | "------ Hey!" |
| 3 | "------ Hey! Wake up!" |

### 动画资源

| 文件 | 用途 |
|------|------|
| `image/image.gif` (320x80) | 像素变换遮罩精灵图（8x2=16帧，40x40/帧） |
| `data/open2.gif` | 日语开篇画面 |
| `data/open3.gif` | 英语开篇画面 |

## 完整事件流程

### 第一阶段：触发与Zeno动画

**触发条件**：玩家走到全局坐标 (31, 9)，`event_3f == 0`，`charaY % 5 == 0`（对齐网格）

**代码位置**：`eventMT` 第3702-3712行

```
条件: charaY%5==0 && 全局X==31 && 全局Y==9 && event_3f==0
```

1. 停止当前BGM
2. **调用 `Zeno(graphics, 31, 7)`** — 在全局坐标 (31, 7)（玩家上方2格）播放Zeno像素变换动画
3. 等待400ms
4. 显示消息10（Zeno的开篇台词）
5. 设置 `event_3f = 1`, `event_counter = 3`

### 第二阶段：勇者反应

**代码位置**：`eventMT` 第3696-3701行

```
条件: event_3f==1 && !messageFlag
```

1. 等待400ms
2. 显示消息222（勇者："What?"）
3. 设置 `event_3f = 2`

### 第三阶段：召唤Madoushi

**代码位置**：`eventMT` 第3683-3695行

```
条件: event_3f==2 && !messageFlag
```

1. 等待400ms
2. **调用 `Madoushi(graphics, 31, 9)`** — 在玩家位置播放Madoushi像素变换动画
3. 在玩家四周放置4个58号怪物：
   - `mapObject[8][31] = 58`（上方）
   - `mapObject[9][30] = 58`（左方）
   - `mapObject[9][32] = 58`（右方）
   - `mapObject[10][31] = 58`（下方）
4. 设置 `event_3f = 3`

### 第四阶段：勇者被攻击

**代码位置**：`eventMT` 第3677-3682行

```
条件: event_3f==3 && !messageFlag
```

1. 等待400ms
2. 显示消息223（勇者："Hey!"）
3. 设置 `event_3f = 4`

### 第五阶段：传送动画与开篇

**代码位置**：`eventMT` 第3622-3659行

```
条件: event_3f==4 && !messageFlag
```

1. 等待400ms
2. 播放音效（sfx 10）
3. 在画面中央(200, 360)绘制角色精灵+闪烁特效，等待600ms
4. 隐藏角色方向（`mapObject[67][119] = 0`）
5. 设置 `flag3F = 1`
6. 设置 `map[9][31] = 116`（在玩家原位置放传送tile）
7. 清除玩家原位置附近的对象（`mapObject[69][119]=0, mapObject[70][119]=0`）
8. 设置 `event_3f = 5`, `event_counter = 5`
9. **调用 `OpenningZeno(graphics, n)`** — 全屏像素变换动画：
   - 英语（language==0）：n=3，使用 `open3.gif`
   - 其他语言：n=2，使用 `open2.gif`
   - 动画持续约6.4秒（16帧 × 400ms）
   - 动画结束后显示最终画面600ms
10. 设置 `flag3F = 1`, `openningFlag = true`
11. 传送玩家到 floor 51：
    - `mapX = 0, mapY = 5`（floor 51）
    - `charaX = 5, charaY = 5`（局部坐标(1,1)）
12. 设置 `mapFlagAll = true`, `mapFlagErase = false`
13. 清除按键状态
14. 设置 `event_counter = 0`（覆盖之前的5）
15. **重置玩家属性**：`HP=400, ATK=10, DEF=10`

### 第六阶段：开篇剧情序列

**代码位置**：`displayConfigWindow` 第13389-13398行 + `eventMT` 第3660-3675行

传送后玩家处于 floor 51（mapX=0, mapY=5），`openningFlag=true`。Floor 51 不在 `FLOOR_MAPS` 中，地图数据全为0（空黑画面）。`paintMapAll` 仍然会被调用（openningFlag 只阻止 `paintMap` 增量绘制和角色渲染，不阻止 `paintMapAll` 全量绘制）。

**驱动机制**：`displayConfigWindow`（状态栏渲染函数，第13389-13398行）检测到 floor 51 时推进 `event_counter`。此函数在 `paintMapAll`（第4137行）中被调用。消息显示时 `mapFlagAll` 被设为 true（第745行），因此每帧都会调用 `paintMapAll` → `displayConfigWindow`。

**event_counter 在 `displayConfigWindow` 中的推进规则**（第13389-13398行）：

| 当前值 | 目标值 | 条件 |
|-------|-------|------|
| 0 | 6 | floor == 51 |
| 6 | 7 | floor == 51 |
| 7 | 8 | floor == 51 |
| 8 | 9 | floor == 51 |

**event_counter 在 `eventMT` 中的处理**（第3660-3675行）：

| 值 | 代码行 | 动作 |
|---|-------|------|
| 6 | 3661-3663 | 显示消息266（"------"） |
| 7 | 3664-3666 | 显示消息2（"------ Hey!"） |
| 8 | 3667-3669 | 显示消息3（"------ Hey! Wake up!"） |
| 9 | 3670-3674 | `flag3F=1`, `openningFlag=false`, `map[66][1]=117`, `BGMset()` |

**逐帧流程**：

| 帧 | event_counter | 发生了什么 |
|----|--------------|-----------|
| 1 | 0→6 | `paintMapAll` → `displayConfigWindow` 推进。随后 `eventMT` 检测到6，显示消息266 |
| 2 | 6（不变） | 消息"------"显示中，`mapFlagAll=true`，`paintMapAll` 执行但 event_counter=6 不匹配任何推进条件 |
| 3 | 6→7 | 用户按Enter关闭消息 → `messageFlag=false` → `paintMapAll` → `displayConfigWindow` 推进6→7。随后 `eventMT` 检测到7，显示消息2 |
| 4 | 7（不变） | 消息"------ Hey!"显示中 |
| 5 | 7→8 | 用户按Enter关闭消息 → 推进7→8 → `eventMT` 显示消息3 |
| 6 | 8（不变） | 消息"------ Hey! Wake up!"显示中 |
| 7 | 8→9 | 用户按Enter关闭消息 → 推进8→9 → `eventMT` 执行: `openningFlag=false`, `map[66][1]=117`, `BGMset()` |

### 第七阶段：自动传送到 Floor 2

**代码位置**：`moveCharacter`（第6374行）→ `pointCheck`（第6312行）

当 event_counter 到达9时：
- `openningFlag = false` → 恢复地图绘制和角色渲染
- `map[66][1] = 117` → 在 floor 51 的玩家脚下放一个传送tile
  - 全局坐标 (1, 66) = 局部坐标 (1, 1) = 玩家位置 (charaX=5, charaY=5)
- `BGMset()` → 播放新BGM

**自动传送机制**：
1. 最后一条消息关闭后，`movingSkip=3`（第747行），3帧内 `moveCharacter` 不执行
2. `paintMapAll` 已执行，`mapFlagAll=false`，`movingSkip` 每帧递减1
3. 约3帧后 `movingSkip=0` → 调用 `moveCharacter` → `pointCheck`
4. `pointCheck` 检查玩家当前位置的tile：`map[66][1]=117`，类型为2（`MAP_LOCALGATE`）
5. 由于 `oldMapData` 不等于117（还是之前在 floor 3 的旧值），不会跳过
6. **自动传送**到 floor 2：
   - `mapX = 17/13 = 1, mapY = 8/13 = 0` → floor 2
   - `charaX = (17%13)*5 = 20, charaY = (8%13)*5 = 40` → 局部 (4, 8)
7. `mapFlagAll=true`, `mapFlagErase=true` → 全量重绘 floor 2

**注意**：传送是自动的，玩家不需要按任何方向键。`pointCheck` 检查的是玩家**当前脚下**的tile，而不是移动目标的tile。

## 像素变换动画原理

### Zeno动画（`Zeno` 方法，第14170-14234行）

**动画位置**：全局坐标 (31, 7) — 玩家上方2格

**使用素材**：
- 遮罩：`image.gif`（320x80，8列x2行=16帧，每帧40x40）
- 背景：地面tile（MAP_ATTR[1] 的 crop1）
- 目标A：57号怪物第1帧（OBJECT_ATTR[57] 的 crop1 = 121）
- 目标B：57号怪物第2帧（OBJECT_ATTR[57] 的 crop2 = 122）

**算法**（16帧，每帧400ms）：
```
透明色 = image.gif 第1帧左上角(0,0)像素的颜色
对每帧 n (1-16):
    col = (n-1) % 8
    row = (n-1) // 8
    从 image.gif 取 (col*40, row*40) 位置的40x40遮罩帧
    if 帧1-8 或 偶数帧:
        目标精灵 = 57号怪物第1帧
    else:
        目标精灵 = 57号怪物第2帧
    对每个像素(x,y):
        if 遮罩像素 == 透明色:
            显示地面颜色
        else:
            显示怪物精灵颜色
    绘制结果到屏幕
```

**动画结束后**：在全局坐标 (31, 9) 放置57号怪物对象 → `mapObject[9][31] = 57`

### Madoushi动画（`Madoushi` 方法，第14306-14371行）

**动画位置**：同时在4个位置绘制（玩家上方、左方、右方、下方）

**使用素材**：
- 遮罩：`image.gif`（同上）
- 背景：地面tile
- 目标A：58号怪物第1帧（OBJECT_ATTR[58] 的 crop1 = 123）
- 目标B：58号怪物第2帧（OBJECT_ATTR[58] 的 crop2 = 124）

**算法**：与Zeno相同，但在4个位置同时绘制相同的结果帧。屏幕坐标：
- 上方：`(n3*40, (n4-1)*40)` — 玩家上方1格
- 左方：`((n3-1)*40, n4*40)` — 玩家左方1格
- 右方：`((n3+1)*40, n4*40)` — 玩家右方1格
- 下方：`(n3*40, (n4+1)*40)` — 玩家下方1格

### OpenningZeno动画（`OpenningZeno` 方法，第14443-14677行）

**动画位置**：全屏（820x520），将开篇图片逐帧用遮罩揭示

**使用素材**：
- 遮罩：`image.gif`
- 背景：地面tile的左上角像素颜色
- 目标：`open2.gif` 或 `open3.gif`（640x400开篇画面）

**算法**（16帧，每帧200ms）：
```
透明色 = image.gif 第1帧左上角像素颜色
背景色 = 地面tile左上角像素颜色
对每帧 n (1-16):
    从 image.gif 取遮罩帧
    对开篇图片的每个40x40格子:
        对格子内每个像素(x,y):
            if 遮罩像素 == 透明色:
                显示背景色
            else:
                显示开篇图片原色
    缩放到820x520显示
```

**动画结束后**：显示原始开篇画面600ms

## 时序图

```
玩家走到(31,9)
    │
    ▼
[Zeno像素变换动画] 16帧×400ms = 6.4秒
    │  动画结束后在(31,9)放置57号怪物(Zeno)
    ▼
显示消息10 → 用户按Enter关闭 (event_3f: 0→1)
    │
    ▼
显示消息222 → 用户按Enter关闭 (event_3f: 1→2)
    │
    ▼
[Madoushi像素变换动画] 16帧×400ms = 6.4秒
    │  在玩家四周放置4个58号怪物
    ▼
显示消息223 → 用户按Enter关闭 (event_3f: 3→4)
    │
    ▼
[玩家闪烁消失] 600ms
    │
    ▼
[OpenningZeno全屏动画] 16帧×200ms + 600ms ≈ 3.8秒
    │
    ▼
传送到floor 51 (黑屏), HP=400, ATK=10, DEF=10
openningFlag=true, event_counter=0
    │
    ▼
Frame 1: displayConfigWindow → event_counter 0→6
         eventMT → 显示消息266 "------"
    │
    ▼ 用户按Enter
Frame 3: displayConfigWindow → event_counter 6→7
         eventMT → 显示消息2 "------ Hey!"
    │
    ▼ 用户按Enter
Frame 5: displayConfigWindow → event_counter 7→8
         eventMT → 显示消息3 "------ Hey! Wake up!"
    │
    ▼ 用户按Enter
Frame 7: displayConfigWindow → event_counter 8→9
         eventMT → openningFlag=false, map[66][1]=117, BGMset()
    │
    ▼ movingSkip=3 → 2 → 1 → 0 (约3帧)
moveCharacter → pointCheck 检测脚下tile 117
    │
    ▼
自动传送到floor 2 局部(4,8), 地图全量重绘
```

## Python版实现注意事项

1. **动画系统**：原版使用同步阻塞动画（`twait`），Python版需要用帧计数器+定时器实现异步动画
2. **事件轮询**：原版 `eventMT` 每帧在 `paint` 中调用，Python版需要在主循环中每帧调用 `poll_3f_events`
3. **event_counter推进**：原版在 `displayConfigWindow` 中推进（检测 floor==51），Python版需要在消息关闭后手动推进
4. **floor 51**：不在 `FLOOR_MAPS` 中，地图数据全为0（空黑），传送后需要特殊处理
5. **开篇序列**：传送后的黑屏+消息序列是游戏的开篇剧情，模拟勇者被击败后"醒来"的场景
6. **自动传送**：`pointCheck` 在 `moveCharacter` 中调用，检查玩家当前脚下tile。楼梯放在玩家脚下后，`movingSkip` 倒计时结束即自动触发传送，无需玩家按键
7. **event_counter==9 持续触发**：原版中 event_counter 到达9后不会被重置，每帧都会执行 `openningFlag=false` + `map[66][1]=117` + `BGMset()`。这是原版的已知问题（不影响游戏），Python版可在传送后手动重置 event_counter
