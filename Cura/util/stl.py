import sys, math, re, os, struct, time

import mesh

class stlModel(mesh.mesh):
	def __init__(self):
		super(stlModel, self).__init__()

	def load(self, filename):
		f = open(filename, "rb")
		if f.read(5).lower() == "solid":
			self._loadAscii(f)
			if self.vertexCount < 3:
				f.seek(5, os.SEEK_SET)
				self._loadBinary(f)
		else:
			self._loadBinary(f)
		f.close()
		
		self._postProcessAfterLoad()
		return self
	
	def _loadAscii(self, f):
		cnt = 0
		for line in f:
			if 'vertex' in line:
				cnt += 1
		self._prepareVertexCount(int(cnt))
		f.seek(5, os.SEEK_SET)
		cnt = 0
		for line in f:
			if 'vertex' in line:
				data = line.split()
				self.addVertex(float(data[1]), float(data[2]), float(data[3]))

	def _loadBinary(self, f):
		#Skip the header
		f.read(80-5)
		faceCount = struct.unpack('<I', f.read(4))[0]
		self._prepareVertexCount(faceCount * 3)
		for idx in xrange(0, faceCount):
			data = struct.unpack("<ffffffffffffH", f.read(50))
			self.addVertex(data[3], data[4], data[5])
			self.addVertex(data[6], data[7], data[8])
			self.addVertex(data[9], data[10], data[11])

def saveAsSTL(mesh, filename):
	f = open(filename, 'wb')
	#Write the STL binary header. This can contain any info, except for "SOLID" at the start.
	f.write(("CURA BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))
	#Next follow 4 binary bytes containing the amount of faces, and then the face information.
	f.write(struct.pack("<I", len(mesh.faces)))
	for face in mesh.faces:
		v1 = face.v[0]
		v2 = face.v[1]
		v3 = face.v[2]
		normal = (v2 - v1).cross(v3 - v1)
		normal.normalize()
		f.write(struct.pack("<fff", normal.x, normal.y, normal.z))
		f.write(struct.pack("<fff", v1.x, v1.y, v1.z))
		f.write(struct.pack("<fff", v2.x, v2.y, v2.z))
		f.write(struct.pack("<fff", v3.x, v3.y, v3.z))
		f.write(struct.pack("<H", 0))
	f.close()

if __name__ == '__main__':
	for filename in sys.argv[1:]:
		m = stlModel().load(filename)
		print("Loaded %d faces" % (m.vertexCount / 3))
#		parts = m.splitToParts()
#		for p in parts:
#			saveAsSTL(p, "export_%i.stl" % parts.index(p))

