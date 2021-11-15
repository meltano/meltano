"""The block module implements and supports the Meltano 'block' architecture.

Currently comprised of:

BlockSet interface spec
- ExtractLoadBlock - a block set implementing basic ELT functionality using lower level IOBlocks.
IOBlock interface spec
- SingerBlock - a IOBlock implementation wrapping singer plugins.
"""
