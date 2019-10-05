package main

import "strconv"

func quadInt2QuadKey(quadint uint64) string {
	var qk string
	zoom := int(quadint & 0b11111)
	
	for i := 0; i < zoom; i++ {
		bit_loc := (64 - ((i + 1) * 2))
		char_bits := ((quadint & (0b11 << bit_loc)) >> bit_loc)
		qk += strconv.Itoa(int(char_bits))
	}

	return qk
}

func quadKey2QuadInt(quadkey string) (uint64, error) {
	var qi uint64
	zoom := len(quadkey)

	for i := 0; i < zoom; i++ {
		bit_loc := (64 - ((i + 1) * 2))
		char, err := strconv.Atoi(string(quadkey[i]))
		if err != nil {
			return 0, err
		}
		qi |= uint64(char) << bit_loc
	}
	qi |= uint64(zoom)

	return qi, nil
}