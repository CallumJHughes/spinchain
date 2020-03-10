!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!  SUBROUTINES DEPENDENCIES !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MODULE dependencies
implicit none

CONTAINS

    include 'BaseGenerator.f90'
    include 'Couplings.f90'
    include 'Couplings_custom.f90'
    include 'Hamiltonian_linear.f90'
    include 'Hamiltonian_star.f90'
    include 'Hamiltonian_custom.f90'
    include 'Dynamics.f90'
    include 'Time_integration.f90'
    include 'Reducedrho.f90'
    include 'Eof.f90'
    include 'Read_fromFile.f90'

END MODULE


