#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "../include/ann_interface.hpp"

namespace py = pybind11;

// Forward declarations for factory functions
extern "C" ANNAlgorithm* create_vectordb_kernel();
extern "C" ANNAlgorithm* create_naive_algorithm();

/**
 * Python wrapper for C++ ANNAlgorithm.
 * Handles numpy array conversion automatically.
 */
class PyANNWrapper {
public:
    PyANNWrapper(const std::string& impl_type, const std::string& metric) {
        if (impl_type == "naive") {
            algo_ = create_naive_algorithm();
        } else if (impl_type == "vectordb") {
            algo_ = create_vectordb_kernel();
        } else {
            throw std::runtime_error("Unknown implementation: " + impl_type);
        }
        metric_ = metric;
    }

    ~PyANNWrapper() {
        delete algo_;
    }

    void fit(py::array_t<float> X) {
        py::buffer_info buf = X.request();
        
        if (buf.ndim != 2) {
            throw std::runtime_error("Input must be 2D array (n_samples, dimension)");
        }
        
        size_t n_samples = buf.shape[0];
        int dimension = buf.shape[1];
        
        algo_->init(metric_, dimension);
        algo_->fit(static_cast<float*>(buf.ptr), n_samples);
    }

    std::vector<int> query(py::array_t<float> v, int k) {
        py::buffer_info buf = v.request();
        
        if (buf.ndim != 1) {
            throw std::runtime_error("Query must be 1D array (dimension,)");
        }
        
        return algo_->query(static_cast<float*>(buf.ptr), k);
    }

    std::vector<std::vector<int>> batch_query(py::array_t<float> X, int k) {
        py::buffer_info buf = X.request();
        
        if (buf.ndim != 2) {
            throw std::runtime_error("Queries must be 2D array (n_queries, dimension)");
        }
        
        size_t n_queries = buf.shape[0];
        return algo_->batch_query(static_cast<float*>(buf.ptr), n_queries, k);
    }

    size_t get_memory_usage() const {
        return algo_->get_memory_usage();
    }

    std::string name() const {
        return algo_->name();
    }

private:
    ANNAlgorithm* algo_ = nullptr;
    std::string metric_;
};

PYBIND11_MODULE(ann_cpp, m) {
    m.doc() = "C++ ANN implementation with Python bindings";

    py::class_<PyANNWrapper>(m, "ANNAlgorithm")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("impl_type"),
             py::arg("metric"),
             "Create ANN algorithm.\n\n"
             "Args:\n"
             "    impl_type: 'naive' or 'vectordb'\n"
             "    metric: 'euclidean' or 'angular'")
        .def("fit", &PyANNWrapper::fit,
             py::arg("X"),
             "Build index from training data.\n\n"
             "Args:\n"
             "    X: numpy array of shape (n_samples, dimension)")
        .def("query", &PyANNWrapper::query,
             py::arg("v"),
             py::arg("k"),
             "Query for k nearest neighbors.\n\n"
             "Args:\n"
             "    v: numpy array of shape (dimension,)\n"
             "    k: number of neighbors\n"
             "Returns:\n"
             "    List of k indices")
        .def("batch_query", &PyANNWrapper::batch_query,
             py::arg("X"),
             py::arg("k"),
             "Batch query for k nearest neighbors.\n\n"
             "Args:\n"
             "    X: numpy array of shape (n_queries, dimension)\n"
             "    k: number of neighbors per query\n"
             "Returns:\n"
             "    List of lists of indices")
        .def("get_memory_usage", &PyANNWrapper::get_memory_usage,
             "Get memory usage in bytes")
        .def("name", &PyANNWrapper::name,
             "Get algorithm name");
}
