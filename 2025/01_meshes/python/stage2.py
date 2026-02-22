import gmsh


def build_mesh(input_stl):
    gmsh.initialize()
    gmsh.model.add("SimpleMesh")
    gmsh.merge(input_stl)
    surfaces = gmsh.model.getEntities(2)
    if not surfaces:
        print("поверхности не найдены!")
        return

    tags = [s[1] for s in surfaces]
    try:
        loop = gmsh.model.geo.addSurfaceLoop(tags)
        gmsh.model.geo.addVolume([loop])
        gmsh.model.geo.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMin", 0.5)
        gmsh.option.setNumber("Mesh.MeshSizeMax", 1)

        gmsh.model.mesh.generate(3)
        gmsh.write("stage2.msh")
        print("сетка готова!")
        gmsh.fltk.run()
    except Exception as e:
        print(f"не удалось создать объем: {e}")

    gmsh.finalize()

build_mesh("stage2.stl")
