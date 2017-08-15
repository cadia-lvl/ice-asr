# Ice-norm - text normalization for Icelandic ASR

A collection of scripts for text normalization of Icelandic texts. The normalization is for the purpose of automatic speech recognition and along with general text cleaning procedures addresses special problems of web scraped texts from news sites. This is a work in progress.

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