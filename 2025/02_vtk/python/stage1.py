import gmsh
import numpy as np
import vtk

class SimpleVibrationMesh:
    def __init__(self, stl_file, mesh_size=1.0):
        self.stl_file = stl_file
        self.mesh_size = mesh_size

        # cоздаем сетку
        self.points = None
        self.tetrahedra = None
        self.base_points = None
        self.center = None
        self.n_points = 0
        self.n_cells = 0

        self.create_mesh()
        print(f"Сетка: {self.n_points} точек, {self.n_cells} тетраэдров")

    def create_mesh(self):
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)

        try:
            gmsh.model.add("Mesh")
            gmsh.merge(self.stl_file)

            surfaces = gmsh.model.getEntities(2)
            tags = [s[1] for s in surfaces]
            loop = gmsh.model.geo.addSurfaceLoop(tags)
            gmsh.model.geo.addVolume([loop])
            gmsh.model.geo.synchronize()

            gmsh.option.setNumber("Mesh.MeshSizeMin", self.mesh_size)
            gmsh.option.setNumber("Mesh.MeshSizeMax", self.mesh_size)

            gmsh.model.mesh.generate(3)

            # точки
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
            self.points = np.array(node_coords, dtype=np.float64).reshape(-1, 3)
            self.base_points = self.points.copy()
            self.n_points = len(self.points)

            #тэтраэдры
            elem_types, _, elem_node_tags = gmsh.model.mesh.getElements()
            for i, elem_type in enumerate(elem_types):
                if elem_type == 4:  # Тетраэдры
                    tet_data = elem_node_tags[i]
                    self.tetrahedra = np.array(tet_data, dtype=np.int32).reshape(-1, 4) - 1
                    self.n_cells = len(self.tetrahedra)
                    break

            self.center = np.mean(self.points, axis=0)

        finally:
            gmsh.finalize()

    def _create_vtk_grid(self, points_array):
        vtk_grid = vtk.vtkUnstructuredGrid()

        vtk_points = vtk.vtkPoints()
        for point in points_array:
            vtk_points.InsertNextPoint(point)
        vtk_grid.SetPoints(vtk_points)

        for tet in self.tetrahedra:
            tetra = vtk.vtkTetra()
            for j in range(4):
                tetra.GetPointIds().SetId(j, int(tet[j]))
            vtk_grid.InsertNextCell(tetra.GetCellType(), tetra.GetPointIds())

        return vtk_grid

    def calculate_velocity(self, point, time, frequency=1.0, amplitude=50.0):
        r_vec = point - self.center
        distance = np.linalg.norm(r_vec)

        if distance > 0:
            direction = r_vec / distance
        else:
            direction = np.array([0, 0, 1])

        # синусоидальная вибрация
        v_mag = amplitude * np.sin(2 * np.pi * frequency * time)

        # зависимость от расстояния
        max_dist = np.max(np.linalg.norm(self.points - self.center, axis=1))
        if max_dist > 0:
            dist_factor = 0.5 + 0.5 * np.sin(distance / max_dist * np.pi)
        else:
            dist_factor = 1.0

        return direction * v_mag * dist_factor

    def calculate_pressure(self, point, time, wave_speed=1.0):
        r_vec = point - self.center
        distance = np.linalg.norm(r_vec)

        # простая бегущая волна
        pressure = np.sin(2.0 * distance - wave_speed * time)

        return pressure

    def create_frame(self, step, time, displacement_factor=0.1):
        """Создает один кадр"""
        new_points = np.zeros_like(self.points)
        velocities = np.zeros_like(self.points)
        pressures = np.zeros(self.n_points)

        # вычисляем для каждой точки
        for i in range(self.n_points):
            point = self.base_points[i]

            # вибрация
            velocity = self.calculate_velocity(point, time)
            velocities[i] = velocity

            # новое положение
            new_points[i] = point + velocity * displacement_factor

            # давление (скалярное поле)
            pressures[i] = self.calculate_pressure(point, time)

        snapshot = self._create_vtk_grid(new_points)

        # векторное поле скорости
        vtk_velocity = vtk.vtkDoubleArray()
        vtk_velocity.SetNumberOfComponents(3)
        vtk_velocity.SetName("Velocity")
        for vel in velocities:
            vtk_velocity.InsertNextTuple3(vel[0], vel[1], vel[2])
        snapshot.GetPointData().AddArray(vtk_velocity)

        # скалярное поле давления
        vtk_pressure = vtk.vtkDoubleArray()
        vtk_pressure.SetName("Pressure")
        for p in pressures:
            vtk_pressure.InsertNextValue(p)
        snapshot.GetPointData().AddArray(vtk_pressure)

        # модуль скорости для окрашивания
        vtk_speed = vtk.vtkDoubleArray()
        vtk_speed.SetName("Speed")
        for vel in velocities:
            speed = np.linalg.norm(vel)
            vtk_speed.InsertNextValue(speed)
        snapshot.GetPointData().AddArray(vtk_speed)

        #сохраняем
        filename = f"frame_{step:04d}.vtu"
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(filename)
        writer.SetInputData(snapshot)
        writer.Write()

        return filename

    def create_animation(self, num_frames=30, dt=0.1):

        print(f"Создание {num_frames} кадров анимации...")

        frame_files = []

        for i in range(num_frames):
            time = i * dt
            filename = self.create_frame(i, time)
            frame_files.append(filename)

            if i % 5 == 0:
                print(f"  Кадр {i + 1}/{num_frames}")
        return frame_files


def main():
    STL_FILE = "../../01_meshes/python/stage2.stl"

    try:
        mesh = SimpleVibrationMesh(STL_FILE, mesh_size=1.0)
        mesh.create_animation(num_frames=30, dt=0.1)
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()