
MODULE parameters

use constants

!**********************
!!INITIAL DEFINITIONS *
!**********************

! Start with a completely custom network
! If this is set, most other topology/coupling settings are ignored
logical                               :: custom            = .false.
integer,                    parameter :: max_string_size   = 1000
integer                               :: coupling_digits   = 4
character(max_string_size)            :: custom_string     = &
  & "<A|C>AB500BC500#00"

! If the program should give a time estimate and then stop
logical :: stop_after_time = .false.
logical :: stop_after_time_full = .false.

! Should the program produce a data file for an animated figure
logical :: create_animation = .false.

!*Define chain topology*!:
!* Check one *!
logical, parameter :: linear = .true.
logical, parameter :: star = .false.
logical, parameter :: lattice = .false.
logical, parameter :: squared = .false.

!*Define couplings scheme*!:
!* Check one *!
logical, parameter :: uniform = .true.
logical, parameter :: pst = .false.
logical, parameter :: ssh_a = .false.
logical, parameter :: ssh_b = .false.
logical, parameter :: abc = .false.
logical, parameter :: kitaev = .false.

!*You want to calculate dynamical figures?*!:
logical :: dynamics = .true. !calculation of dynamics
logical :: single = .false.  !single point calculation

!*You want to read the initial state from file?*!:
logical, parameter :: read_state = .false. !read from previous final state

!*What method do you wish to use to solve the Schrodinger eq.?*!:
logical, parameter :: integration = .false.
logical, parameter :: diagonalisation = .true.

!*Define presence of disorder*!:
logical, parameter :: random_J = .false. !Off-diagonal disorder
logical, parameter :: random_D = .false. !Diagonal disorder

!*Manage files*!:
logical :: output = .true.
logical :: files = .true.
logical :: graphical = .true.

!*************************************!
!   Genetic algorithm parameters      !
!*************************************!

! Should a genetic algorithm be used to perfect the coupling strengths?
logical                   :: use_genetic              = .false.

! Number of networks being tested each generation
integer                   :: genomes_per_generation   = 1024
integer                   :: max_generations          = 200

! Mutation parameters, increasing these increases search space
integer                   :: num_initial_mutations    = 5
real(kind=dbl), parameter :: mutate_chance            = 1.0_dbl
integer                   :: mutate_amount_initial    = -1
integer                   :: mutate_amount_final      = 1
integer                   :: mutate_amount            = -1
integer                   :: max_val                  = -1
integer, parameter        :: min_val                  = 1

! Should the algorithm stop after a certain fidelity is reached
real(kind=dbl)            :: stop_after_fid           = -1

! Should the alternating crossover method be used?
logical,        parameter :: use_alternating          = .true.

! Should a bogo method be used for testing?
logical :: use_bogo = .false.

! Should the fitness function be linear with fidelity?
logical                   :: linear_fitness           = .false.
logical                   :: force_fitness            = .false.

! Should only on-site energies be optimised
logical                   :: energies_only            = .false.

! Should negative couplings be allowed?
logical                   :: allow_negative           = .false.

! Max fidelity search range
real(kind=dbl)            :: min_time                 = 0.0_dbl  
real(kind=dbl)            :: max_time                 = 20.0_dbl  

! Should time be minimised along with the fidelity?
logical                   :: minimise_time            = .true.

! Fitness function scaling factors, don't touch these
real(kind=dbl), parameter :: fidelity_scale           = 10.0_dbl    
real(kind=dbl)            :: time_scale               = -0.001_dbl  

!**************************************
!!Basic characteristics of the system *
!**************************************

integer            :: N = 4            ! Size of the system
integer            :: exno = 1         ! Total number of excitations
integer, parameter :: branches = 1     ! Number of branches, if linear set to 1.

! The initial/target excitation vectors and their sizes
! GO TO BOTTOM TO DEFINE THESE
integer                                        :: numModes = 1    
integer                                        :: numI = 1    
integer                                        :: numF = 1   
complex(kind=dbl), dimension(:,:), allocatable :: initialCoeff
complex(kind=dbl), dimension(:,:), allocatable :: targetCoeff
integer, dimension(:,:), allocatable           :: initialVec  
integer, dimension(:,:), allocatable           :: targetVec
integer, dimension(:,:,:), allocatable         :: initVectorFull
integer, dimension(:,:,:), allocatable         :: finalVectorFull

!**********************
!!Coupling parameters *
!**********************

real(kind=dbl), parameter :: J_max = 1.0    !Maximum coupling in the middle
                                            !for PST. Used also when uniform
real(kind=dbl), parameter :: J_strong = 1.0 !Strong versus weak coupling for
real(kind=dbl), parameter :: J_weak = 0.1   !SSH-like schemes.

real(kind=dbl) :: eeScale = 0.1410          !Scaling factor for excite-excite interaction

!************************************
!!Disorder and tolerance parameters *
!************************************

!*For average purposes*!:
integer, parameter        :: num_realisations = 1 !How many noise realisations (1 by default)

real(kind=dbl), parameter :: E_J = 1.0_dbl  !scale of the disorder on the couplings, in units of J_max
real(kind=dbl), parameter :: E_D = 0.10_dbl !scale of the disorder on the sites, in units of J_max

real(kind=dbl), parameter :: error=0.0001_dbl !allowed error for integration method and normalisation checks

!**********************
!!Dynamics parameters *
!**********************

integer, parameter :: steps = 100
real(kind=dbl) :: totalTime = 20 !total time for the dynamics
real(kind=dbl) :: t_A = 4  !time for single point calculation (set single option)


!****************
!!Entanglements *
!****************

!choose your measure
logical, parameter :: eof = .true.
logical, parameter :: max_eof = .true. !calculates the maximum eof over
                                      !a time window = totalTime

!qubits to trace for EOF
integer, parameter :: Q1 = 3
integer, parameter :: Q2 = 4


!****************
!!INITIAL STATE *
!****************

contains

subroutine initialState(initialVec)

    integer, dimension(:,:), allocatable, intent(inout) :: initialVec

    ! Number of different modes
    numModes = 1

    ! Number of initial and final injections
    numI = 1
    numF = 1

    ! allocate the arrays
    if (allocated(initialVec)) deallocate(initialVec)
    allocate(initialVec(numModes, numI))
    if (allocated(targetVec)) deallocate(targetVec)
    allocate(targetVec(numModes, numF))

    ! The initially injected vectors
    initialVec(1,1) = 2

    ! The desired target for fitness/plotting
    targetVec(1,1) = 1+N

    !!Keep adding vectors in this fashion and with this same numenclature
    !!Normalisation is done automatically
    !!Overall initial State = norm*[initialVec(1)+...+intialVec(numI)]

end subroutine initialState

END MODULE
