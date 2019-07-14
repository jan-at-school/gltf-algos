from prettyprinter import pprint
from pygltflib import GLTF2, Node, BufferFormat
import numpy as np
# import matplotlib.pyplot as plt
import transformations
import base64
import mimetypes
import warnings
import os

# https://model-generator-rkvilcygba-uc.a.run.app/convertScaleAndUploadMeshes?inputFilePath=users/2y7aPImLYeTsCt6X0dwNMlW9K5h1/mesh/meshGLTF_2019-07-07T10:27:49.380Z_6l4XZ8V8w.glb&inputFileType=GLB&outputGLBPath=users/2y7aPImLYeTsCt6X0dwNMlW9K5h1/mesh/meshGLTF_2019-07-07T10:27:51.990Z_oWRsuPlx0.glb&outputUSDZPath=users/2y7aPImLYeTsCt6X0dwNMlW9K5h1/mesh/meshUSDZ_2019-07-07T10:27:51.990Z_QcGCoggAGg.usdz&inputBucketURI=digibaad-dev44.appspot.com&outputBucketURI=digibaad-dev44.appspot.com&length=7&width=3&height=3










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

            if gltf.nodes[i].children[j] > index:
                gltf.nodes[i].children[j] += 1
    for i in range(len(gltf.scenes)):
        for j in range(len(gltf.scenes[i].nodes)):
            if gltf.scenes[i].nodes[j] > index:
                gltf.scenes[i].nodes[j] += 1

'''
resons to not use:
order of rotation...needs first node to be skipped
'''
def composeMatrixFromMatrixAndTRS(matrix, T=[0,0,0], R=[0, 0, 0, 1], S=[1,1,1]):

    print('matrix',matrix)
    print('T',T)
    print('R',R)
    print('S',S)


    R = transformations.euler_from_quaternion(R,'sxyz')

    trs = transformations.compose_matrix(
        S, None, R, T)

    
    matrix = np.array(matrix)
    matrix.shape = (4,4)
    newMatrix = np.dot(trs, matrix)
    return newMatrix


def composeMatrixFromTRS(translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
    
    a = np.dot(translation,rotation)
    a = np.dot(a,scale)
    return a



myMin=[10000000, 10000000, 10000000]
myMax=[-10000000, -10000000, -10000000]
def dimensionsOLD(gltf, node, parentMatrix=transformations.scale_matrix(1)):
    # pprint(node)

    T = node.translation or [0, 0, 0]
    R = node.rotation or [0, 0, 0, 1]
    S = node.scale or [1, 1, 1]
    # thisNodeMatrix =  composeMatrixFromTRS(T,R,S)

    R = transformations.euler_from_quaternion(R,'sxyz')

    thisNodeMatrix = node.matrix or transformations.compose_matrix(
        S, None, R, T)

        
    thisNodeMatrix = np.array(thisNodeMatrix)
    thisNodeMatrix.shape = (4,4)
    
    newMatrix = np.dot(thisNodeMatrix,parentMatrix)

    if node.mesh != None:
        accessor = gltf.accessors[gltf.meshes[node.mesh]
                                  .primitives[0].attributes.POSITION]


        possiblities = [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1],
        ]
        testMin = accessor.min
        testMax = accessor.max

        for test in possiblities:
            test = [
                testMin[0] if test[0] == 0 else testMax[0],
                testMin[1] if test[1] == 0 else testMax[1],
                testMin[2] if test[2] == 0 else testMax[2],
            ]
            print("=======",node.name)
            print('before',test)
            test = np.matmul(test + [1],newMatrix )
            scale, shear, angles, trans, persp = transformations.decompose_matrix(newMatrix)
            print("by matrix",np.multiply(angles,57))
            print('after',test)
            

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


    for child in node.children:
        dimensionsOLD(gltf, gltf.nodes[child], newMatrix)




def convertImages(gltf, bufferType):
    for i in range(len(gltf.images)):
        
        imageUri = gltf.images[i].uri
        if imageUri == None:
            continue
        if imageUri.startswith('data:'):
           # no need
           print('no need to convert')
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





# ORIGINAL_FILE = 'res/lucifers_corvette_-_1960_chevrolet_corvette_c1.glb'
ORIGINAL_FILE = 'res/lucifers_corvette_-_1960_chevrolet_corvette_c1/scene.gltf'
ORIGINAL_FILE = 'res/Buggy.glb'
ORIGINAL_FILE = 'res/mini_cooper_s/scene.gltf'
# ORIGINAL_FILE = 'res/2CylinderEngine.glb'
# ORIGINAL_FILE = 'res/box.glb'

def rad(degrees):
    return degrees * 0.0174533


gltf = GLTF2().load(ORIGINAL_FILE)
# gltf.nodes[0].scale = [1,1,1]

node = Node()
node.name = '1'
node.children = [1]
insertNode(gltf,0,node)

# gltf.nodes[0].rotation = transformations.quaternion_from_euler(rad(0),rad(0),rad(45)).tolist()



# node2 = Node()
# node2.name = '2'
# node2.children = [1]
# insertNode(gltf,0,node2)

# gltf.nodes[0].scale = [1,2,1]

# gltf.nodes[0].translation = [1,0,1]


# gltf.nodes[0].rotation = transformations.quaternion_from_euler(45,45,0).tolist()


dimensionsOLD(gltf,gltf.nodes[0])
boundingBox = np.subtract(myMax, myMin)
scale =  [1,1,1]
print("min ",myMin)
print("max",myMax)
print("BoundingBox",boundingBox)




newScale = [1/boundingBox[0],1/boundingBox[1],  1/boundingBox[2]]
nodeToOverride = gltf.nodes[0]

matrix = nodeToOverride.matrix if len(nodeToOverride.matrix) != 0 else transformations.scale_matrix(1)
rotation = nodeToOverride.rotation if len(nodeToOverride.rotation) != 0 else [0,0,0,1]
translation = nodeToOverride.translation if len(nodeToOverride.translation) != 0 else [0, 0, 0]


newScale = np.multiply(newScale,nodeToOverride.scale if len(nodeToOverride.scale) != 0 else [1,1,1])
# newMatrix = composeMatrixFromMatrixAndTRS(matrix,translation,rotation,newScale)
# nodeToOverride.matrix = None
# nodeToOverride.scale = None
# nodeToOverride.translation = None
# nodeToOverride.rotation = None
# print("matriiix", transformations.decompose_matrix(newMatrix))
# newMatrix.shape = (16)
# nodeToOverride.matrix = newMatrix.tolist()
# print("Scale",gltf.nodes[0].matrix)



nodeToOverride.scale = newScale.tolist()
print("Scale",gltf.nodes[0].scale)


convertImages(gltf,BufferFormat.DATAURI)  
gltf.convert_buffers(BufferFormat.BINARYBLOB)
gltf.save('res/output/output.glb')


gltf.convert_buffers(BufferFormat.DATAURI)
# convertImages(gltf,BufferFormat.DATAURI) // not needed see above
gltf.save('res/output/output.gltf')


