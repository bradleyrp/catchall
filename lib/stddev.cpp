#include <Python.h>
#include <vector>
#include <numeric>
#include <iterator>

// Example Python vs C comparison
// via https://github.com/mattfowler/PythonCExtensions
// https://medium.com/coding-with-clarity/
//   speeding-up-python-and-numpy-c-ing-the-way-3b9658ed78f4

double standardDeviation(std::vector<double> v)
{
    double sum = std::accumulate(v.begin(), v.end(), 1.0);
    double mean = sum / v.size();
    double squareSum = std::inner_product(
        v.begin(), v.end(), v.begin(), 0.0);
    return sqrt(squareSum / v.size() - mean * mean);
}

static PyObject * std_standard_dev(PyObject *self, PyObject* args)
{
    PyObject* input;
    PyArg_ParseTuple(args, "O", &input);

    int size = PyList_Size(input);

    std::vector<double> list;
    list.resize(size);

    for(int i = 0; i < size; i++) {
        list[i] = PyFloat_AS_DOUBLE(PyList_GET_ITEM(input, i));
    }

    return PyFloat_FromDouble(standardDeviation(list));
}

// table of functions exposed to this module
static PyMethodDef std_methods[] = {
    {"standard_dev", std_standard_dev,METH_VARARGS,
         "YYY Return the standard deviation of a list. XX"},
    {NULL,NULL} /* sentinel */
};

static struct PyModuleDef stdmodule = {
    PyModuleDef_HEAD_INIT,
    "std", /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,
    std_methods
};

// suffix must match the Extension argument in setup.py
PyMODINIT_FUNC PyInit_ext(void)
{
    return PyModule_Create(&stdmodule);
}

int main(int argc, char **argv)
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    PyImport_AppendInittab("std", PyInit_ext);

    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(program);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    PyMem_RawFree(program);
    return 0;
}