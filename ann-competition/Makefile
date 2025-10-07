.PHONY: help setup build clean test benchmark quick compare

help:
	@echo "ANN Competition - Available Commands"
	@echo "===================================="
	@echo "  make setup      - Initial setup (install dependencies with uv)"
	@echo "  make build      - Build C++ code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make quick      - Quick test on synthetic data"
	@echo "  make test       - Run full test suite"
	@echo "  make benchmark  - Run full benchmark on GIST dataset"
	@echo "  make compare    - Compare student vs naive implementation"
	@echo ""
	@echo "Modal Commands (for remote execution):"
	@echo "  make modal-build     - Build on Modal"
	@echo "  make modal-benchmark - Run benchmark on Modal"

setup:
	@echo "Installing dependencies with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync
	@echo "✓ Setup complete"

build:
	@echo "Building C++ extensions..."
	@mkdir -p build
	cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$$(nproc)
	@echo "✓ Build complete"

build-debug:
	@echo "Building with debug symbols..."
	@mkdir -p build
	cd build && cmake .. -DCMAKE_BUILD_TYPE=Debug && make -j$$(nproc)
	@echo "✓ Debug build complete"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build
	rm -rf python/ann_competition/*.so
	rm -rf python/ann_competition/__pycache__
	rm -rf results/*
	@echo "✓ Clean complete"

quick: build
	@echo "Running quick test..."
	uv run python scripts/quick_test.py --impl student

test: build
	@echo "Running test suite..."
	uv run python scripts/quick_test.py --impl naive
	uv run python scripts/quick_test.py --impl student

benchmark: build
	@echo "Running full benchmark..."
	uv run python scripts/benchmark.py --impl student --output results/benchmark_$$(date +%Y%m%d_%H%M%S).json

compare: build
	@echo "Comparing implementations..."
	uv run python scripts/benchmark.py --impl student --compare naive

# Modal commands (if modal is available)
modal-build:
	modal run dev_on_modal.py --command=build

modal-benchmark:
	modal run dev_on_modal.py --command=benchmark

# Development helpers
format:
	@echo "Formatting C++ code..."
	find src include -name "*.cpp" -o -name "*.hpp" | xargs clang-format -i
	@echo "✓ Format complete"

check-build:
	@if [ ! -d "build" ]; then \
		echo "Build directory not found. Run 'make build' first."; \
		exit 1; \
	fi

.PHONY: help setup build clean test benchmark quick compare modal-build modal-benchmark format check-build
