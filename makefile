# Define directories
src = src
plot = src/Plotting
bin = bin

# Define variables
wrapper = $(bin)/wrapper.o
main = $(src)/main.f90
gen = $(src)/genetic.f90
const = $(src)/CONSTANTS.f90
param = $(src)/PARAMETERS.f90
depen = $(src)/DEPENDENCIES.f90

# Compilers
f90comp = mpifort
Pycomp = python3

# Libraries
libs = -lblas -llapack

# Install directory
installDir = "/usr/share/spinnet"
binDir = "/usr/bin/"

# Flags to use
flagsFast = -O3 -march=native
flagsDebug = -g -Wall -fcheck=all -pg
#flags = $(flagsDebug)
flags = $(flagsFast)

# Compile fortran first create bin, then execute
running: clean | $(bin) exec moving

dependancies:
	apt install mpich gfortran python3 liblapack-dev libblas-dev python3-tk libopenblas-dev python3-matplotlib python3-numpy python3-pil make

# Global installation
install:
	@echo "Installing to $(installDir)"
	rm -rf $(installDir)
	mkdir $(installDir)
	cp -r $(bin)/* $(installDir)/
	@echo "Add $(installDir) to your path to use spinnet from anywhere"

uninstall:
	@echo "Removing $(installDir)"
	rm -rf $(installDir)
	rm -f $(binDir)/spinnet
	rm -f $(binDir)/spinnet-vis

# Execute procedure, first Fortran and then Python
exec: $(wrapper)
	$(f90comp) $(bin)/c.o $(bin)/p.o $(bin)/d.o $(bin)/g.o $(bin)/m.o $(wrapper) -o run $(flags) $(libs)

# Move binaries to the bin folder
moving:
	cp $(src)/*.py $(bin)/
	mv run $(bin)/run
	cp $(src)/spinnet $(bin)/spinnet
	cp $(src)/spinnet-vis $(bin)/spinnet-vis
	cp -r $(src)/*.png $(bin)/
	rm -f *.mod
	rm -f $(bin)/*.o

# Create bin
$(bin):
	mkdir -p $(bin)

# Compile programs, first modules
$(bin)/wrapper.o: $(src)/wrapper.f90
	$(f90comp) -c $(const) -o $(bin)/c.o $(flags) $(libs)
	$(f90comp) -c $(param) -o $(bin)/p.o $(flags) $(libs)
	$(f90comp) -c $(depen) -o $(bin)/d.o $(flags) $(libs)
	$(f90comp) -c $(main) -o $(bin)/m.o $(flags) $(libs)
	$(f90comp) -c $(gen) -o $(bin)/g.o $(flags) $(libs)
	$(f90comp) -c $^ -o $@ $(flags)

# Clean
clean:
	rm -f run 
	rm -f *.mod
	rm -fr $(bin)
	rm -f $(src)/*.o
