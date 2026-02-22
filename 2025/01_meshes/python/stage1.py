import gmsh
import sys

# инициализация
gmsh.initialize()
gmsh.model.add("Tokamak_Torus")

# ядро OpenCASCADE для булевых операций
occ = gmsh.model.occ

# параметры
R_major = 1.0      # расстояние от центра тора до центра трубки
R_minor_out = 0.4  # внешний радиус трубки
R_minor_in = 0.3   # внутренний радиус трубки

# толщина стенки получается 0.1 (0.4 - 0.3)
wall_thickness = R_minor_out - R_minor_in

# настройка сетки
# Чтобы в стенку влезло 4 тетраэдра, размер одного должен быть ~ толщина / 4
lc = wall_thickness / 4.0

# создание геометрии
outer = occ.addTorus(0, 0, 0, R_major, R_minor_out)
inner = occ.addTorus(0, 0, 0, R_major, R_minor_in)

# вычитаем из внешнего тора внутренний
occ.cut([(3, outer)], [(3, inner)])
occ.synchronize()

gmsh.option.setNumber("Mesh.MeshSizeMin", lc)
gmsh.option.setNumber("Mesh.MeshSizeMax", lc)
gmsh.model.mesh.generate(3)
gmsh.write("hollow_torus.msh")

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()