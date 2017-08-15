# Ice-norm - text normalization for Icelandic ASR

A collection of scripts for normalization of Icelandic texts. The normalization is for the purpose of language model building for automatic speech recognition. Punctuation is removed, some common abbreviations and acronyms replaced and all text is lowercased. Along with these general text cleaning procedures, the project addresses special problems of web scraped texts from Icelandic news sites. This is a work in progress, issues like digits and dates have not been attacked at all for example.

Example:

Input:

	Sjö þeirra eru frá Þýskalandi, einn frá Bretlandi og einn frá Suður-Kóreu.
	Helga Friðfinnsdóttir, framkvæmdastjóri Happdrættis SÍBS, segir að erfitt yrði að greiða meira fyrir leyfið til happdrættisreksturs en nú er.
	Þau mótmæli verða milli 12 og 13. Ritstjórn DV (ritstjorn@dv.
	Innlent - 8. maí 2008, 12:46 Geysir Green mátti kaupa Jarðborun Forsíða..
	
Output:

	sjö þeirra eru frá þýskalandi einn frá bretlandi og einn frá suður kóreu
	helga friðfinnsdóttir framkvæmdastjóri happdrættis s í b s segir að erfitt yrði að greiða meira fyrir leyfið til happdrættisreksturs en nú er
	þau mótmæli verða milli 12 og 13
	- 8 maí 2008 1246 geysir green mátti kaupa jarðborun