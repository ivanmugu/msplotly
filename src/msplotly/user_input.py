"""Class to store information provided by user for plotting.

License
-------
This file is part of MSPlotly
BSD 3-Clause License
Copyright (c) 2024, Ivan Munoz Gutierrez
"""

from pathlib import Path

from typing import Union


class UserInput:
    """Store information provided by user for plotting."""

    def __init__(
        self,
        input_files: Union[list[Path], None] = None,
        output_folder: Union[None, Path] = None,
        alignments_position: Union[None, str] = None,
        identity_color: Union[None, str] = None,
        colorscale_vmin: Union[None, float] = None,
        colorscale_vmax: Union[None, float] = None,
        set_colorscale_to_extreme_homologies: Union[None, bool] = None,
        annotate_sequences: Union[None, bool] = None,
        annotate_genes: Union[None, bool] = None,
        annotate_genes_with: Union[None, str] = None,
        straight_homology_regions: Union[None, bool] = None,
        minimum_homology_length: Union[None, int] = None,
        add_scale_bar: Union[None, bool] = None,
    ):
        self.input_files = input_files
        self.output_folder = output_folder
        self.alignments_position = alignments_position
        self.identity_color = identity_color
        self.colorscale_vmin = colorscale_vmin
        self.colorscale_vmax = colorscale_vmax
        self.set_colorscale_to_extreme_homologies = set_colorscale_to_extreme_homologies
        self.annotate_sequences = annotate_sequences
        self.annotate_genes = annotate_genes
        self.annotate_genes_with = annotate_genes_with
        self.straight_homology_regions = straight_homology_regions
        self.minimum_homology_length = minimum_homology_length
        self.add_scale_bar = add_scale_bar
