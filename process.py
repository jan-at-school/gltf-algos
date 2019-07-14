def insertNode(gltf, index, node):
    pprint(node)
    gltf.nodes.insert(index, node)
    print('Nodes: ', len(gltf.nodes))

    for i in range(len(gltf.nodes)):

        print('Node: ', i)
        pprint(gltf.nodes[i])

        if i == index or gltf.nodes[i].children == None:
            continue

        for j in range(len(gltf.nodes[i].children)):

            if gltf.nodes[i].children[j] >= index:
                gltf.nodes[i].children[j] += 1


def composeMatrixFromMatrixAndTRS(matrix, translation=[0]*3, rotation=[0, 0, 0, 1], scale=None):
    translation = numpy.array(translation)
    rotation = numpy.array(rotation)
    scale = numpy.array(scale)

    return scale


def composeMatrixFromTRS(translation=None, rotation=None, scale=None):
    translation
    rotation
    scale

    return scale


def dimensions(gltf, node, parentMatrix=transformations.scale_matrix(1), myMin=[10000000, 10000000, 10000000], myMax=[-10000000, -10000000, -10000000]):
    # pprint(node)

    T = node.translation or [0, 0, 0]
    R = node.rotation or [0, 0, 0, 1]
    S = node.scale or [1, 1, 1]

    R = transformations.euler_from_quaternion(R)

    thisNodeMatrix = node.matrix or transformations.compose_matrix(
        S, None, R, T)

    newMatrix = np.dot(parentMatrix, thisNodeMatrix)

    if node.mesh != None:
        accessor = gltf.accessors[gltf.meshes[node.mesh]
                                  .primitives[0].attributes.POSITION]

        testMin = accessor.min
        testMax = accessor.max

        # testMin = np.matmul(newMatrix,accessor.min + [1] )
        # testMax = np.matmul(newMatrix,accessor.max + [1])

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

    print('New Matrix', newMatrix)
    for child in node.children:
        dimensions(gltf, gltf.nodes[child], newMatrix,myMin,myMax)


def convertImages(gltf, bufferType):
    for i in range(len(gltf.images)):
        imageUri = gltf.images[i].uri

        if imageUri.startswith('data:'):
            if(bufferType == BufferFormat.BINARYBLOB):
                gltf.images[i].uri = gltf.images[i].uri.encode()
            elif bufferType == BufferFormat.DATAURI:
                gltf.images[i].uri = gltf.images[i].uri.decode('utf-8')
        else:

            path = os.path.dirname(ORIGINAL_FILE) + '/' + imageUri
            # print(path)

            mime, _ = mimetypes.guess_type(path)

            with open(path, "rb") as image_file:

                encoded_string = str(base64.b64encode(
                    image_file.read()).decode('utf-8'))
                gltf.images[i].uri = 'data:{mime};base64,{encoded}'.format(
                    mime=mime, encoded=encoded_string)

                if(bufferType == BufferFormat.BINARYBLOB):
                    print('Encoding to binary')
                    gltf.images[i].uri = gltf.images[i].uri.encode()





def process():
