!=========================================================================!
! Subroutine that returns an array with the couplings for a given         !
! network string                                                          !
!-------------------------------------------------------------------------!
! Parameters                                                              !
!   Js2D         : array to save the coupling data                        !
!   N_local      : number of nodes                                        !
!   string       : network string to use                                  !
!-------------------------------------------------------------------------!
! Written by Luke Mortimer October 2019                                   !
!=========================================================================!
subroutine couplings_custom(Js2D, N_local, string)

    use parameters
    use constants

    ! Inputs 
    integer, intent(in)   :: N_local
    character(*)          :: string

    ! Outputs
    real(kind=dbl), dimension(N_local,N_local), intent(out) :: Js2D

    ! The mapping of chars to node indices
    character, dimension(:), allocatable :: uniqueChars

    ! For holding the indices and coupling strengths from the string
    integer :: a_index, b_index, val

    ! For temporarily holding the string containing the coupling value
    character(20) :: val_string
    integer :: val_count

    ! Loop counters
    integer :: i, j

    ! Assume all zero until otherwise
    Js2D = 0.0_dbl

    ! Get the mapping of letters to numbers
    call get_char_map(string, uniqueChars)

    ! Iterate over the string
    do i = 1, len_trim(string), 2 + coupling_digits

        ! Reset everything
        a_index = -1
        b_index = -1
        val_string = ""
        val_count = 0

        ! Get the indices of the characters
        do j = 1, size(uniqueChars, 1)
            if (uniqueChars(j) == string(i:i)) a_index = j
            if (uniqueChars(j) == string(i+1:i+1)) b_index = j
        end do

        ! Get the coupling value
        val = chars_to_int(string(i+2:i+coupling_digits+1))

        ! The value is negative if the characters are in the wrong order
        if (ichar(string(i:i)) > ichar(string(i+1:i+1))) then
            val = -val
        end if

        ! Set the couplings, ensuring symmetry
        Js2D(a_index, b_index) = val
        Js2D(b_index, a_index) = val

    end do

    ! Normalise
    Js2D = Js2D / maxval(Js2D)

    ! Go through the diagonals, if any are zero then set to default
    do i = 1, N_local
        if (abs(Js2D(i,i)) < tiny(0.0_dbl)) then
            Js2D(i,i) = 1.0_dbl
        end if
    end do

end subroutine

!=========================================================================!
! Convert a string of chars to an integer e.g. "32" -> 32                 !
!-------------------------------------------------------------------------!
! Parameters                                                              !
!   chars       : string of chars to convert                              !
!-------------------------------------------------------------------------!
! Returns an integer                                                      !
!-------------------------------------------------------------------------!
! Written by Luke Mortimer October 2019                                   !
!=========================================================================!
function chars_to_int(chars)

    character(*), intent(in) :: chars
    integer :: chars_to_int
    character(10) :: format_string

    ! Generate the format string, since can't do I0 reads on a string
    write(format_string, "(A,I0,A)") "(I", len_trim(chars), ")"

    ! Read the chars as an integer
    read(chars, format_string) chars_to_int

end function

!=========================================================================!
! Convert a string of chars to a real e.g. "3.2" -> 3.2                   !
!-------------------------------------------------------------------------!
! Parameters                                                              !
!   chars       : string of chars to convert                              !
!-------------------------------------------------------------------------!
! Returns an real                                                         !
!-------------------------------------------------------------------------!
! Written by Luke Mortimer October 2019                                   !
!=========================================================================!
function chars_to_real(chars)

    character(*), intent(in) :: chars
    real :: chars_to_real
    character(20) :: format_string

    integer :: digitsAfter, i

    ! See if there's a "." and if so, where?
    if (scan(chars, ".") > 0) then
        digitsAfter = len_trim(chars) - index(chars, ".")
    else
        digitsAfter = 0
    end if

    ! Generate the format string, since can't do I0 reads on a string
    write(format_string, "(A,I0,A,I0,A)") "(F", len_trim(chars), ".", digitsAfter, ")"

    ! Read the chars as an integer
    read(chars, format_string) chars_to_real

end function

!=========================================================================!
! Return an array containing the unique letters in a string               !
!-------------------------------------------------------------------------!
! Parameters                                                              !
!   string  : string of chars to get the letters from                     !
!   N       : number of unique letters                                    !
!-------------------------------------------------------------------------!
! Returns a char array                                                    !
!-------------------------------------------------------------------------!
! Written by Luke Mortimer October 2019                                   !
!=========================================================================!
subroutine get_char_map(string, map)

    use parameters 

    character(*), intent(in) :: string
    character, dimension(:), allocatable, intent(out) :: map
    character, dimension(max_string_size):: temp_char_map
    integer :: numUniqueChars

    integer :: i, j
    logical :: found

    ! Map the letters in the string to node numbers (ADGZ -> 1,2,3,4)
    temp_char_map = ""
    numUniqueChars = 0
    do i = 1, len_trim(string)

        ! Skip the letter if it's a digit or a dash
        if (scan(string(i:i), "0123456789-i+.()[]>") > 0) cycle

        ! See if the letter is unique
        found = .false.
        do j = 1, numUniqueChars
            if (temp_char_map(j) == string(i:i)) then
                found = .true.
            end if
        end do

        ! If it wasn't in the array, add it
        if (.not. found) then
            numUniqueChars = numUniqueChars + 1
            temp_char_map(numUniqueChars) = string(i:i)
        end if

    end do

    if (allocated(map)) deallocate(map)
    allocate(map(numUniqueChars)) 
    map(1:numUniqueChars) = temp_char_map(1:numUniqueChars)

end subroutine

!=========================================================================!
! Processes any directives within brackets in a custom string             !
!-------------------------------------------------------------------------!
! Parameters                                                              !
!   string       : the custom string to read/modify                       !
!   init_direct  : optional, return the removed init->final directive     !
!   pos_direct   : optional, return the removed positional directives     !
!-------------------------------------------------------------------------!
! Written by Luke Mortimer October 2019                                   !
!=========================================================================!
subroutine process_directives(string, init_direct, pos_direct)

    use constants
    use parameters

    ! The given string to modify
    character(max_string_size), intent(inout) :: string

    ! If present, return the removed directives
    character(max_string_size), intent(inout), optional :: init_direct, pos_direct

    ! The various temporary strings used for processing the directives
    character(max_string_size) :: substring, time_direct_string
    character(max_string_size), dimension(:), allocatable :: from_string, to_string

    ! The stored character map (from chars to node index)
    character, dimension(:), allocatable :: map

    ! Keep track of where the brackets start
    integer :: bracket_start 

    ! Temp variable storing where the arrow (->) is in the substring
    integer :: pipe_index

    ! Loop counters
    integer :: i, j, k, mode_counter

    ! Keep track of how many initial/final vectors 
    integer :: numFCount, numICount, plusCount

    ! For figuring out the coefficients of each excitation
    character(20) :: coeff_substring
    logical :: in_brackets, in_time_direct

	!------------------------------------------------------------------------------
	logical :: zero_direct
	!------------------------------------------------------------------------------

    ! If present, reset the return vals
    if (present(init_direct)) init_direct = ""
    if (present(pos_direct)) pos_direct = ""

    ! Ignore the positional directive
    i = index(string, "#")
    if (i > 0) then
        if (present(pos_direct)) pos_direct = string(i:)
        string = trim(string(:i-1))
    end if

    ! Count the number of different exicitation/target pairs
    numModes = 0
    mode_counter = 0
    do i = 1, len_trim(string)
        if (string(i:i) == "|") numModes = numModes + 1
    end do

    ! Allocate the arrays of substrings based on how many modes required
    if (allocated(to_string)) deallocate(to_string)
    allocate(to_string(numModes))
    if (allocated(from_string)) deallocate(from_string)
    allocate(from_string(numModes))
    time_direct_string = ""

    ! Loop over the chars in the string (i may be modified in the loop)
    i = 1
    do while (i <= len_trim(string))

        ! If found the start of a initial|target directive
        if (string(i:i) == "<") then

            ! Make note of where the brackets start
            bracket_start = i

        ! If finishing with a initial->target directive
        else if (string(i:i) == ">") then

            mode_counter = mode_counter + 1

            ! Now determine the initial and target injections
            substring = trim(string(bracket_start+1:i-1))
            pipe_index = index(substring, "|")
            from_string(mode_counter) = trim(substring(1:pipe_index-1)) 
            to_string(mode_counter) = trim(substring(pipe_index+1:))

            ! If arg present, update this directive
            if (present(init_direct)) init_direct = trim(init_direct) // trim(string(bracket_start:i))

            ! Remove this directive from the main string
            if (bracket_start > 1) then
                string = trim(string(1:bracket_start-1)) // trim(string(i+1:)) 
            else
                string = trim(string(i+1:))
            end if

            ! Move i back since the string has changed
            i = bracket_start - 1

        end if

        i = i + 1

    end do

	! Add 00 state feature here
	!----------------------------------------------------------------------------------------------------------------------------
	zero_direct = .FALSE.
	do while (i <= len_trim(string))
		if (string(i:i) == char(37)) then
			zero_direct = .TRUE.
		end if
	end do

	print *, "ZERO DIRECTIVE:", zero_direct
	!----------------------------------------------------------------------------------------------------------------------------

    i = 1
    in_time_direct = .false.
    bracket_start = 0
    do while (i <= len_trim(string))

        if (string(i:i) == "@") then

            in_time_direct = .true.
            bracket_start = i

            ! Remove this char from the string
            string = trim(string(:i-1)) // trim(string(i+1:))
            i = i - 1

        else if (in_time_direct .and. ((ichar(string(i:i)) >= 48 .and. ichar(string(i:i)) <= 57) .or. string(i:i) == ".")) then

            time_direct_string = trim(time_direct_string) // trim(string(i:i))

            ! Remove this char from the string
            string = trim(string(:i-1)) // trim(string(i+1:))
            i = i - 1

        else

            in_time_direct = .false.

        end if

        i = i + 1

    end do

    ! Get the time for single point
    if (len_trim(time_direct_string) >= 1) then
        if (present(init_direct)) init_direct = "@" // trim(time_direct_string) // trim(init_direct)
        t_A = chars_to_real(time_direct_string)
        single = .true.
    end if

    ! Get the character map 
    call get_char_map(string, map)

    ! Set N depending on the number of unique chars
    N = size(map, 1)

    ! Get the number of initial and target exicitations
    numI = 1
    numF = 1
    do i = 1, numModes

        ! Count the plusses in the initial section
        plusCount = 0
        in_brackets = .false.
        do j = 2, len_trim(from_string(i))
            if (scan(from_string(i)(j:j), "+-") > 0 .and. .not. in_brackets) plusCount = plusCount + 1
            if (from_string(i)(j:j) == "(") in_brackets = .true.
            if (from_string(i)(j:j) == ")") in_brackets = .false.
        end do
        if (plusCount + 1 > numI) numI = plusCount + 1

        ! Count the plusses in the final section
        plusCount = 0
        in_brackets = .false.
        do j = 2, len_trim(to_string(i))
            if (scan(to_string(i)(j:j), "+-") > 0 .and. .not. in_brackets) plusCount = plusCount + 1
            if (to_string(i)(j:j) == "(") in_brackets = .true.
            if (to_string(i)(j:j) == ")") in_brackets = .false.
        end do
        if (plusCount + 1 > numF) numF = plusCount + 1

    end do

    ! Allocate the arrays
    if (allocated(initialVec)) deallocate(initialVec)
    if (allocated(targetVec)) deallocate(targetVec)
    if (allocated(initialCoeff)) deallocate(initialCoeff)
    if (allocated(targetCoeff)) deallocate(targetCoeff)
    if (allocated(initVectorFull)) deallocate(initVectorFull)
    if (allocated(finalVectorFull)) deallocate(finalVectorFull)
    allocate(initialVec(numModes, numI))
    allocate(targetVec(numModes, numF))
    allocate(initialCoeff(numModes, numI))
    allocate(targetCoeff(numModes, numF))
    allocate(initVectorFull(numModes, numI, N))
    allocate(finalVectorFull(numModes, numF, N))

    ! Init things
    initVectorFull = 0
    finalVectorFull = 0
    initialCoeff = cmplx(1.0_dbl, 0.0_dbl, dbl)
    targetCoeff = cmplx(1.0_dbl, 0.0_dbl, dbl)
    coeff_substring = ""
    in_brackets = .false.

    ! For each mode
    do i = 1, numModes

        numICount = 1
        numFCount = 1

        ! Go through each char on the left of the divider
        do j = 1, len_trim(from_string(i))

            ! If a normal character, add that component to the desired vector
            if (scan(".0123456789()+-i", from_string(i)(j:j)) == 0) then

                ! Find that char in the char to state map
                do k = 1, N
                    if (map(k) == from_string(i)(j:j)) then
                        initVectorFull(i, numICount, k) = 1
                        exit
                    end if
                end do

            ! Otherwise, if a minus (only if first), a plus (only in brackets) or anything else
            else if ((from_string(i)(j:j) == "-" .and. j == 1) .or. scan(from_string(i)(j:j), "+-") == 0&
                        &  .or. in_brackets) then

                coeff_substring = trim(coeff_substring) // trim(from_string(i)(j:j))
                if (from_string(i)(j:j) == "(") in_brackets = .true.
                if (from_string(i)(j:j) == ")") in_brackets = .false.

            end if

            ! If at the end or at a +, add the current substring as a init vector
            if (j == len_trim(from_string(i)) .or. (scan(from_string(i)(j:j), "+-") > 0 .and. .not. in_brackets .and. j > 1)) then

                ! If needed, increase the number of excitations required
                if (sum(initVectorFull(i, numICount, :)) > exno) then
                    exno = sum(initVectorFull(i, numICount, :))
                end if

                ! Also set the coefficient for this excitation
                if (len_trim(coeff_substring) > 0) then
                    initialCoeff(i, numICount) = string_to_complex(coeff_substring)
                    coeff_substring = ""
                end if

                ! If adding because of a minus, add the minus to the next elements coeff substring
                if (from_string(i)(j:j) == "-") then
                    coeff_substring = "-"
                end if

                numICount = numICount + 1

            end if

        end do

        ! Go through each char on the right of the divider
        do j = 1, len_trim(to_string(i))

            ! If a normal character, add that component to the desired vector
            if (scan(".0123456789()+-i", to_string(i)(j:j)) == 0) then

                ! Find that char in the char to state map
                do k = 1, N
                    if (map(k) == to_string(i)(j:j)) then
                        finalVectorFull(i, numFCount, k) = 1
                        exit
                    end if
                end do

            ! Otherwise, if a minus (only if first), a plus (only in brackets) or anything else
            else if ((to_string(i)(j:j) == "-" .and. j == 1) .or. scan(to_string(i)(j:j), "+-") == 0&
                        &  .or. in_brackets) then

                coeff_substring = trim(coeff_substring) // trim(to_string(i)(j:j))
                if (to_string(i)(j:j) == "(") in_brackets = .true.
                if (to_string(i)(j:j) == ")") in_brackets = .false.

            end if

            ! If at the end or at a +, add the current substring as a init vector
            if (j == len_trim(to_string(i)) .or. (scan(to_string(i)(j:j), "+-") > 0 .and. .not. in_brackets .and. j > 1)) then

                ! If needed, increase the number of excitations required
                if (sum(finalVectorFull(i, numFCount, :)) > exno) then
                    exno = sum(finalVectorFull(i, numFCount, :))
                end if

                ! Also set the coefficient for this excitation
                if (len_trim(coeff_substring) > 0) then
                    targetCoeff(i, numFCount) = string_to_complex(coeff_substring)
                    coeff_substring = ""
                end if

                ! If adding because of a minus, add the minus to the next elements coeff substring
                if (to_string(i)(j:j) == "-") then
                    coeff_substring = "-"
                end if

                numFCount = numFCount + 1


            end if

        end do

        ! Since it was easier to start on 1 rather than 0
        numICount = numICount - 1
        numFCount = numFCount - 1

        ! Normalise the vectors
        initialCoeff(i, 1:numICount) = initialCoeff(i, 1:numICount) / &
            & sqrt(sum(initialCoeff(i, 1:numICount)*conjg(initialCoeff(i, 1:numICount))))
        targetCoeff(i, 1:numFCount) = targetCoeff(i, 1:numFCount) / &
            & sqrt(sum(targetCoeff(i, 1:numFCount)*conjg(targetCoeff(i, 1:numFCount))))

    end do

end subroutine

! Given the vectors, find their indices in the array and set
subroutine get_vector_indices(allVectors)

    use constants
    use parameters

    ! The array containing all vectors
    integer, dimension(:,:), intent(in) :: allVectors

    ! Loop counters
    integer :: i, j, k, l

    ! Keeping track of if the vectors match or not
    logical :: isMatch

    initialVec = 0
    targetVec = 0

    ! For each mode
    do l = 1, numModes

        ! For each vector
        do i = 1, size(allVectors, 1)

            ! For each init vector
            do j = 1, numI

                ! See if the two vectors match
                isMatch = .true.
                do k = 1, N
                    if (initVectorFull(l, j, k) /= allVectors(i, k)) then
                        isMatch = .false.
                    end if
                end do

                ! If its a match, set the initial vector index to this
                if (isMatch) initialVec(l, j) = i

            end do

            ! For each final vector
            do j = 1, numF

                ! See if the two vectors match
                isMatch = .true.
                do k = 1, N
                    if (finalVectorFull(l, j, k) /= allVectors(i, k)) then
                        isMatch = .false.
                    end if
                end do

                ! If its a match, set the initial vector index to this
                if (isMatch) targetVec(l, j) = i

            end do

        end do 

    end do 

end subroutine

function string_to_complex(string)

    use constants

    character(*), intent(in) :: string
    character(len(string)) :: string_stripped, substring
    complex(kind=dbl) :: string_to_complex
    integer :: i, j, k
    logical :: is_imag
    real(kind=dbl) :: a, b, a_temp, b_temp

    ! Strip the leading/trailing brackets if needed
    string_stripped = string
    if (string_stripped(1:1) == "(") string_stripped = trim(string_stripped(2:))
    j = len_trim(string_stripped)
    if (string_stripped(j:j) == ")") string_stripped = trim(string_stripped(:j-1))
    j = len_trim(string_stripped)

    ! Initialise
    substring = ""
    a = 0.0_dbl
    b = 0.0_dbl
    a_temp = 0.0_dbl
    b_temp = 0.0_dbl

    ! Loop over the string
    do i = 1, j

        ! Add to the substring
        if (scan(string_stripped(i:i), "+") == 0) then
            substring = trim(substring) // string_stripped(i:i)
        end if

        ! If at the end or at a plus
        if (i == j .or. scan(string_stripped(i:i), "+-") > 0) then

            ! See if this is an imaginary component
            is_imag = .false.
            do k = 1, len_trim(substring)

                if (substring(k:k) == "i") then
                    is_imag = .true.
                    substring = trim(substring(1:k-1)) // trim(substring(k+1:))
                end if

            end do

            ! If it was just i, change to 1
            if (substring == "" .and. is_imag) substring = "1"

            ! Read into the corresponding section (a+ib)
            if (is_imag) then
               read(substring, *) b_temp
               b = b + b_temp
            else
               if (trim(substring) == "-") substring = "-1"
               read(substring, *) a_temp
               a = a + a_temp
            end if

            substring = ""

        end if

    end do

    ! Combine the two reals to make a complex
    string_to_complex = cmplx(a, b, dbl)

end function
