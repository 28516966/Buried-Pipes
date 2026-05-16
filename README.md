# Buried-Pipes
Analysis tools for the design of buried pipes. 

## Traffic Pressures
Executable file:  'buried_pipes_traffic_pressures.exe'

Enables the calculation of live loading traffic surcharge Ps for structural design of buried pipes. Pressures may be calculated for any arbitrary set of point loads. 
Utility is also provided to enable fast discretisation of wheel contact pressures into a set of equivalent point loads.

The implemented calculation methodology is based upon the simplified method outlined by Young and O'Reilly (1983) and Young and Trott (1984) whose charts are reproduced in the design standard BS 9295 for construction vehicle loading.

This method involves the calculation of vertical earth pressures using Boussinesq's formula for point loads (widely available in reference texts). The pressures for each point load comprising the vehicle loading are superimposed on a finite element grid (discretising space across x, y, depth) and the pressures averaged over a line of elements along a set length of pipe (recommended 1m).

## References
- British Standards Institution (2023). BS 9295 AMD 1. Guide to the Structural Design of Buried Pipelines.
- Nath, P. (1981). Pressures on Buried Pipes Due to Revised HB Loading.
- National Highways. (2025). CD 533 V1.2.0 Determination of pipe and bedding combinations for drainage works.
- Young, O.C. and O’Reilly, M.P. (1983). A Guide to Design Loadings for Buried Rigid Pipes.
- Young, O. and Trott, J. (1984). Buried Rigid Pipes. CRC Press.
