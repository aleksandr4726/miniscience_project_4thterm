from fenics import *
import os

# Моделирование нестационарного теплопереноса с внутренним источником тепла
# Решается уравнение теплопроводности u_t - Δu = f(x, t)
# Граничные условия: u = 0 на всей границе (холодные стенки)
T = 2.0            # final time
num_steps = 80     # number of time steps
dt = T / num_steps # time step size

nx = ny = 60
mesh = UnitSquareMesh(nx, ny)
V = FunctionSpace(mesh, 'P', 1)

# Define boundary condition
u_D = Constant(0.0)

def boundary(x, on_boundary):
    return on_boundary

bc = DirichletBC(V, u_D, boundary)


# начальное условие: в начальный момент температура равна нулю
u_n = interpolate(u_D, V)
#источник тепла: локальный нагреватель в центре области
A = 10.0 # мощность
sigma2 =  0.02  #
omega = 3.14159 #

# функция источника f(x,y,t)
f = Expression(
    "A*exp(-((x[0]-0.5)*(x[0]-0.5) + (x[1]-0.5)*(x[1]-0.5))/sigma2)",
    degree=2,
    A=A,
    sigma2=sigma2,
    omega=omega,
    t=0.0
)

u = TrialFunction(V)
v = TestFunction(V)

dt_c = Constant(dt)
kappa = Constant(0.01)
F = u*v*dx + dt_c*kappa*dot(grad(u), grad(v))*dx - (u_n + dt_c*f)*v*dx
a, L = lhs(F), rhs(F)
os.makedirs("heat", exist_ok=True)
res_file = File("heat/solution.pvd")

u = Function(V)
t = 0.0

for n in range(num_steps):
    f.t = t   # обновляем время в источнике тепла
    solve(a == L, u, bc)  # решаем задачу для текущего шага времени
    res_file << (u,t)
    u_n.assign(u)
    t += dt
