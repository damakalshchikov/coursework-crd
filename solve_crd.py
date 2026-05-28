import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve_banded

# Параметры задачи
v = 0.5 # скорость конвекции, м/с
D = 0.1 # коэффициент диффузии, м²/с
k = 0.2 # константа скорости реакции первого порядка, 1/с

x_left  = -2.0 # левая граница области, м
x_right = 10.0 # правая граница области, м
T       = 5.0  # конечный момент времени, с

# Параметры сетки
N  = 600                     # число пространственных интервалов
M  = 2000                    # число временных шагов
dx = (x_right - x_left) / N # шаг по пространству: 0.02 м
dt = T / M                   # шаг по времени: 0.0025 с

# Массивы узлов
x = np.linspace(x_left, x_right, N + 1)

# Начальное условие
c = np.exp(-x**2)

# Аналитическое решение
def c_exact(x, t):
    if t == 0.0:
        return np.exp(-x**2)
    denom = 1.0 + 4.0 * D * t
    return np.exp(-k * t) / np.sqrt(denom) * np.exp(-(x - v * t)**2 / denom)

# Коэффициенты схемы Кранка–Николсон
alpha = D * dt / (2.0 * dx**2) # диффузионный параметр
beta  = v * dt / (4.0 * dx)    # конвективный параметр
gamma = k * dt / 2.0           # реакционный параметр

# Матрица A
#   ab[0, j] = элемент наддиагонали  A[j-1, j] = -(alpha - beta)
#   ab[1, j] = диагональный элемент  A[j, j]   = 1 + 2*alpha + gamma
#   ab[2, j] = элемент поддиагонали  A[j+1, j] = -(alpha + beta)
n_inner = N - 1                   # число внутренних узлов
ab = np.zeros((3, n_inner))
ab[0, 1:]  = -(alpha - beta)      # наддиагональ
ab[1, :]   =  1 + 2*alpha + gamma # главная диагональ
ab[2, :-1] = -(alpha + beta)      # поддиагональ

# Временная интеграция
plot_times = [0.0, 1.0, 2.0, 3.0, 5.0] # моменты для записи профилей
snapshots  = {}   # словарь: t -> (c_численное, c_аналитическое)

def record(t_val, c_num):
    snapshots[t_val] = (c_num.copy(), c_exact(x, t_val))

record(0.0, c)

for n in range(M):
    ci = c[1:-1]   # значения во внутренних узлах на слое n

    # Правая часть системы: вектор B * c^n
    # B: поддиагональ = (alpha+beta),
    #    главная      = (1 - 2*alpha - gamma),
    #    наддиагональ = (alpha - beta)
    rhs = np.zeros(n_inner)

    # Первый внутренний узел:
    rhs[0] = ((1 - 2*alpha - gamma) * ci[0]
              + (alpha - beta) * ci[1])

    # Внутренние узлы:
    rhs[1:-1] = ((alpha + beta) * ci[:-2]
                 + (1 - 2*alpha - gamma) * ci[1:-1]
                 + (alpha - beta) * ci[2:])

    # Последний внутренний узел:
    rhs[-1] = ((alpha + beta) * ci[-2]
               + (1 - 2*alpha - gamma) * ci[-1])

    # Решение системы
    c_new_inner = solve_banded((1, 1), ab, rhs)

    # Сборка полного вектора с граничными условиями c = 0
    c_new = np.zeros(N + 1)
    c_new[1:-1] = c_new_inner
    c = c_new

    # Запись среза при достижении контрольного момента
    t_cur = (n + 1) * dt
    for pt in plot_times:
        if pt not in snapshots and abs(t_cur - pt) < dt / 2:
            record(pt, c)

# Визуализация результатов
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Решение уравнения конвекции–реакции–диффузии", fontsize=13)

# Левый график: профили концентрации в разные моменты времени
ax = axes[0]
colors = plt.cm.plasma(np.linspace(0.1, 0.85, len(plot_times)))
for i, pt in enumerate(plot_times):
    c_num, c_an = snapshots[pt]
    ax.plot(x, c_an,  color=colors[i], lw=2.0,
            label=f"t = {pt} с (аналит.)")
    ax.plot(x, c_num, color=colors[i], lw=1.5, ls="--",
            label=f"t = {pt} с (числен.)")
ax.set_xlabel("x, м")
ax.set_ylabel("c(x, t)")
ax.set_title("Профили концентрации примеси")
ax.legend(fontsize=7.5, ncol=2)
ax.set_xlim(x_left, x_right)
ax.set_ylim(-0.05, 1.1)
ax.grid(True, alpha=0.3)

# Правый график: убывание максимальной концентрации
ax2 = axes[1]
t_arr = np.linspace(0.0, T, 500)
c_max_both = np.exp(-k * t_arr) / np.sqrt(1.0 + 4.0 * D * t_arr)
c_max_diff = 1.0 / np.sqrt(1.0 + 4.0 * D * t_arr) # только диффузия (k=0)
c_max_rxn  = np.exp(-k * t_arr)                    # только реакция (D=0)
ax2.plot(t_arr, c_max_both, "k-",  lw=2.0,
         label="Оба эффекта (диффузия + реакция)")
ax2.plot(t_arr, c_max_diff, "b--", lw=1.5,
         label="Только диффузия ($k=0$)")
ax2.plot(t_arr, c_max_rxn,  "r:",  lw=1.5,
         label="Только реакция ($D=0$)")
ax2.set_xlabel("t, с")
ax2.set_ylabel("max c(x, t)")
ax2.set_title("Убывание максимальной концентрации")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("images/crd_solution.png", dpi=150, bbox_inches="tight")
plt.show()

# Таблица максимальных абсолютных погрешностей
print(f"\n{'t, с':>6} | {'max |c_числ - c_аналит|':>25}")
print("-" * 35)
for pt in plot_times[1:]:
    c_num, c_an = snapshots[pt]
    err = np.max(np.abs(c_num - c_an))
    print(f"{pt:>6.1f} | {err:>25.2e}")
