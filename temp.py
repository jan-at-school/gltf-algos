
def dimensions(gltf, index, parentMatrix=transformations.scale_matrix(1), myMin=[10000000, 10000000, 10000000], myMax=[-10000000, -10000000, -10000000]):
    node = gltf.nodes[index]
    print("\n\n---------------------------Node_---------------------------------")
    T = node.translation if len(node.translation) != 0 else  [0, 0, 0]
    R = node.rotation if len(node.rotation) != 0 else  [0, 0, 0, 1]
    S = node.scale if len(node.scale) != 0 else  [1, 1, 1]

    R = transformations.euler_from_quaternion(R)
    
    
    print(S,np.multiply(R,57.2958),T)
    thisNodeMatrix = node.matrix or transformations.compose_matrix(
        S, None, R, T)


    # pprint(parentMatrix)
    # pprint(thisNodeMatrix)
    thisNodeMatrix = np.array(thisNodeMatrix)
    thisNodeMatrix.shape = (4,4)
    # newMatrix = np.dot(parentMatrix, thisNodeMatrix)
    newMatrix = np.dot( thisNodeMatrix,parentMatrix)


    scale, shear, angles, trans, persp = transformations.decompose_matrix(newMatrix)
    print('New Matrix: ',scale,np.multiply(angles,57.2958),trans)

    if node.mesh != None:
        accessor = gltf.accessors[gltf.meshes[node.mesh]
                                  .primitives[0].attributes.POSITION]

        testMin = accessor.min
        testMax = accessor.max

        print(testMin)
        print(testMax)
        print("AFTER MULTIPLY")
        testMin = np.matmul(newMatrix,accessor.min + [1] )
        testMax = np.matmul(newMatrix,accessor.max + [1])

        print(testMin)
        print(testMax)

        for test in [testMin, testMax]:
            myMin[0] = test[0] if test[0] < myMin[0] else myMin[0]
            myMin[1] = test[1] if test[1] < myMin[1] else myMin[1]
            myMin[2] = test[2] if test[2] < myMin[2] else myMin[2]

            myMax[0] = test[0] if test[0] > myMax[0] else myMax[0]
            myMax[1] = test[1] if test[1] > myMax[1] else myMax[1]
            myMax[2] = test[2] if test[2] > myMax[2] else myMax[2]

    if node.children == None or len(node.children) == 0:
        # pprint(thisNodeMatrix)
        # print(node.mesh)
        return

    # print('New Matrix', newMatrix)
    for child in node.children:
        dimensions(gltf, child, newMatrix,myMin,myMax)

    return myMin,myMax
