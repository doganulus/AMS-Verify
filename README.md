AMS-Verify
==========

### People

Developer: Dogan Ulus

Contributors: Alper Sen, Faik Baskaya

### Abstract

AMS-Verify is an analog and mixed-signal (AMS) verification framework inspired from unit testing methodology in software verification. AMS-Verify framework provides common routines and analyses which extensively used in AMS verification. The structure of AMS-Verify framework is similar to unittest module of standard Python library, which has a rich heritage as part of the xUnit family of testing libraries.

AMS-Verify framework provides a unified environment for assertion-based AMS verification flow. The framework is written in Python language, and consists of three main elements: (i) Assertion checker, (ii) Waveform calculator and (iii) Scientific Python libraries. Assertion checker needs an input file specifying assertions to be checked and we explain details of input file structure in Section 5.1 of my thesis. After assertion checking process is explained in Section 5.2  of my thesis, a True/False answer is produced. Waveform calculator processes simulation data according to commands coming from the assertion checker, and produces a database including results and evaluation steps. This is handy to understand why and where an assertion fails. We developed waveform calculator as a separate unit to allow to work with different waveform calculators, and initially we only support the waveform calculator EzWave. Finally, Python offers several scientific libraries, which can be very useful for high-level analog and mixed-signal verification. In critical parts of our framework, we employ scientific routines such as signal smoothing and Fast Fourier Transform (FFT) algorithms. Existence of these scientific libraries is the determinant factor for the language selection for our framework besides flexible and clean syntax of Python. Therefore, users are free to use these scientific libraries and standard Python constructs in assertion specification.

###Notes

Developed for the partial fulfillment of the requirements for the degree of Master of Science in Bogazici University.
