#import "@preview/arkheion:0.1.0": arkheion, arkheion-appendices
#show: arkheion.with(
  title: [Woolworm: \ A Python Package for Digitizing Historical Documents and Archives],
  authors: (
    (name: "Aerith Netzer", email: "aerith.netzer@northwestern.edu", affiliation: "Northwestern University Libraries", orcid: "0000-0000-0000-0000"),
  ),
  // Insert your abstract after the colon, wrapped in brackets.
  // Example: `abstract: [This is my abstract...]`
  abstract: [Digitization is a core practice in librarianship, particularly in academic universities with very large, often physical archives. Traditional software packages built for this task make the assumption that most steps can be completed by hand. Northwestern University Libraries recently received a grant to digitize approximately 3.5 million pages of Environmental Impact Statements in a two-year timeline. This time compression created a new need in the library: end-to-end automation of image processing and optical character recognition workflows. With the recent rise of transformer-based architectures, we created a high-level Python library called _Woolworm_, a user-friendly library for conditional image binarization, de-skewing, and text extraction. Further, this architecture was built for use with SLURM on high-performance computing clusters. Increasing data throughput and ensuring high availability.],
  keywords: ("OCR", "Digital Libraries", "High-Performance Computing"),
  date: "September 19, 2025",
)

=  Image Processing Pipeline

There are three main steps in the image processing pipeline where it concerns digitization of historical documents: de-skewing, conditional binarization, and border removal. To meet these technical needs, we adopted OpenCV@bradskigOpenCVLibrary2000 for its wide compatibility and long history in the computer vision community.

== Image DeSkewing

In automated scanning machines, individual pages in the film-based medium are often rotated. We correct for this by first applying a bitwise operation, inverting the colors to black/white. We then instantiate a $30 times 1$ rectangular kernel and apply a closing operation on the image. This returns a text line mask, highlighting candidate text lines. We then compute the Shannon entropy of the mask:

$
H = -sum p(x)log_2p(x)
$


If $H$ is a relatively high value, we assume that the content of the page is mostly text. If $H$ is a relatively low value, we assume it is the contrary case.

$A(H) := cases(
  0 "if" H <= T,
  1"else" H > T,
)$

Currently, we are limited to empirical estimation of an optimal $T$ value for entropy threshold. Future work should focus on algorithmic optimization of $T$ threshold.

If $T = 1$, we assume that the image consists of mostly text, and we therefore perform Canny Edge detection and identify Hough Lines from those edges.

If $T = 0$, we assume that the image consists mostly of non-text elements, and we must therefore choose a different method for calculating the document's angular offset from the horizontal.



#bibliography("my-library.bib")
