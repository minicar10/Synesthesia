#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/*
Packet format (16 bytes, big-endian):
byte 0: version (currently 1)
byte 1: red
byte 2: green
byte 3: blue
byte 4-7: track hash (uint32)
byte 8-15: detection timestamp in ms (uint64)
*/

static PyObject *pack_rgb_payload(PyObject *self, PyObject *args) {
    unsigned int r = 0;
    unsigned int g = 0;
    unsigned int b = 0;
    unsigned int track_hash = 0;
    unsigned long long detect_ms = 0;
    unsigned char buf[16];

    if (!PyArg_ParseTuple(args, "BBBIK", &r, &g, &b, &track_hash, &detect_ms)) {
        return NULL;
    }

    buf[0] = 1;
    buf[1] = (unsigned char)r;
    buf[2] = (unsigned char)g;
    buf[3] = (unsigned char)b;

    buf[4] = (unsigned char)((track_hash >> 24) & 0xFF);
    buf[5] = (unsigned char)((track_hash >> 16) & 0xFF);
    buf[6] = (unsigned char)((track_hash >> 8) & 0xFF);
    buf[7] = (unsigned char)(track_hash & 0xFF);

    buf[8] = (unsigned char)((detect_ms >> 56) & 0xFF);
    buf[9] = (unsigned char)((detect_ms >> 48) & 0xFF);
    buf[10] = (unsigned char)((detect_ms >> 40) & 0xFF);
    buf[11] = (unsigned char)((detect_ms >> 32) & 0xFF);
    buf[12] = (unsigned char)((detect_ms >> 24) & 0xFF);
    buf[13] = (unsigned char)((detect_ms >> 16) & 0xFF);
    buf[14] = (unsigned char)((detect_ms >> 8) & 0xFF);
    buf[15] = (unsigned char)(detect_ms & 0xFF);

    return PyBytes_FromStringAndSize((const char *)buf, sizeof(buf));
}

static PyMethodDef PayloadMethods[] = {
    {
        "pack_rgb_payload",
        (PyCFunction)pack_rgb_payload,
        METH_VARARGS,
        "Pack (r,g,b,track_hash,detect_ms) into a compact 16-byte payload."
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef payloadmodule = {
    PyModuleDef_HEAD_INIT,
    "payload_ext",
    "C extension for compact RGB metadata packet packing.",
    -1,
    PayloadMethods
};

PyMODINIT_FUNC PyInit_payload_ext(void) {
    PyObject *module = PyModule_Create(&payloadmodule);
    if (module == NULL) {
        return NULL;
    }
    if (PyModule_AddIntConstant(module, "PACKET_SIZE", 16) < 0) {
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
