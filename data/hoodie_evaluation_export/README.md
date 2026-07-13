# HOODIE evaluation figure export

This bundle contains the five numbered evaluation figures (Figures 7-11), their 15 plotted panels, and digitized data reconstructed from the vector graphics in the supplied PDF.

## Important accuracy note

The paper does not provide its original raw simulation files. Numeric CSV values are **vector-digitized approximations**, not author-released source data. They are generally suitable for reproducing axes, trends, rough baselines, test fixtures, and code contracts, but they must not be presented as exact original measurements. Re-run HOODIE in the shared codebase to obtain authoritative values.

- Figure 7 topology is reconstructed directly from the vector graph and exported as an edge list and adjacency matrix.
- Figures 8-11 are digitized from plotted paths/bars.
- Average delay is negative in the base article by convention.
- Figure 10 delay panels use a 10-second timeout, while drop-ratio panels use a 2-second timeout except the timeout sweep itself.

## ECHO claim policy

ECHO is designed primarily to improve **task drop ratio**, especially under high arrival load, limited CPU, and tight deadlines. The most defensible target panels are Figures 10d, 10e, and 10f. Raw accumulated reward panels cannot be compared directly if ECHO and HOODIE use different reward definitions. No ECHO result is included in this bundle because the ECHO simulator has not yet been executed.
