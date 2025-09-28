class ChordChart {
    constructor() {

        this.imageTop = 1;
        this.imageLeft = 1;

        this.topGutterHeight = 50;
        this.leftGutterWidth = 50;
        this.rightMarginWidth = 20;
        this.bottomMarginHeight = 20;

        this.nutTop = 0;
        this.nutHeight = 10;
        this.nutBottom = 0;

        this.fretboardTop = 0;
        this.fretboardLeft = 0;

        this.stringSpacing = 30;
        this.fretSpacing = 30;

        this.stringCount = 6;

        this.fretCount = 5;

        this.strings = [];
        this.frets = [];

        this.fretboardWidth = 0;
        this.fretboardHeight = 0;

        this.totalImageHeight = 0;
        this.totalImageWidth = 0;

        this.chordName = '';
        this.chordNameLeft = 0;
        this.chordNameTop = 0;

        this.indicatorHeight = 0;
        this.indicatorOffSet = 0;

        this.indicatorLabels = ['X', 'O', 'T', '1', '2', '3', '4'];
    }

    setTop(value) {
        this.imageTop = value;
        return this;
    }

    calculateDimensions() {
        this.nutTop = this.imageTop + this.topGutterHeight;

        this.nutBottom = this.nutTop + this.nutHeight;

        this.fretboardTop = this.nutBottom + 1;
        this.fretboardLeft = this.leftGutterWidth;

        for (let string = 0; string < this.stringCount; ++string) {
            this.strings.push(string);
        }

        for (let fret = 0; fret < this.fretCount; ++fret) {
            this.frets.push(fret);
        }

        this.fretboardWidth = this.stringSpacing * (this.strings.length - 1);
        this.fretboardHeight = this.fretSpacing * this.frets.length;

        this.totalImageHeight = this.topGutterHeight + this.nutHeight + this.fretboardHeight + this.bottomMarginHeight;
        this.totalImageWidth = this.leftGutterWidth + this.fretboardWidth + this.rightMarginWidth;

        this.chordNameLeft = this.fretboardLeft;
        this.chordNameTop = Math.floor(this.topGutterHeight / 2);

        this.indicatorOffSet = -1 * Math.floor(this.fretSpacing / 4);
    }

    createGridChart(data = []) {
        this.calculateDimensions();

        let template = `
            <svg width="${this.totalImageWidth}" height="${this.totalImageHeight}">
                <text x="${this.chordNameLeft}" y="${this.chordNameTop}" fill="black">${this.chordName}</text>
                <rect y="${this.nutTop}" x="${this.fretboardLeft}" width="${this.fretboardWidth}" height="${this.nutHeight}" style="fill:rgb(0,0,0);stroke-width:1;stroke:rgb(0,0,0);"/>
                <rect x="${this.fretboardLeft}" y="${this.fretboardTop}" width="${this.fretboardWidth}" height="${this.fretboardHeight}" style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);"/>
                ${this.getFretsSvg()}
                ${this.getStringsSvg()}
                ${this.getOpenStringsSvg(data)}
                ${this.getFrettedNotesSvg(data)}
            </svg>`;

        return template;
    }

    getFretsSvg() {
        let fretString = '';
        for (let fret of this.frets) {
            let fretPosition = this.fretboardTop + ((fret + 1) * this.fretSpacing);
            fretString += `<line x1="${this.fretboardLeft}" y1="${fretPosition}" x2="${this.fretboardLeft + this.fretboardWidth}" y2="${fretPosition}" style="stroke:rgb(0,0,0);stroke-width:1;"/>`;
        }
        return fretString;
    }

    getStringsSvg() {
        let stringString = '';
        for (let string of this.strings) {
            let stringPosition = string * this.stringSpacing;
            stringString += `<line x1="${this.fretboardLeft + stringPosition}" y1="${this.fretboardTop}" x2="${this.fretboardLeft + stringPosition}" y2="${this.fretboardTop + this.fretboardHeight}" style="stroke:rgb(0,0,0);stroke-width:1;"/>`;
        }
        return stringString;
    }

    getOpenStringsSvg(data) {
        let openStrings = '';
        for (let [index, dataPoint] of data.entries()) {
            let stringPosition = index * this.stringSpacing;
            if (dataPoint[0] === 'O') {
                openStrings += `<circle cx="${this.fretboardLeft + stringPosition}" cy="40" r="5" stroke="black" stroke-width="2" fill="white" />`;
            } else if (dataPoint[0] === 'X') {
                openStrings += `<text x="${this.fretboardLeft + stringPosition - 5}" y="46" fill="black">X</text>`;
            }
        }
        return openStrings;
    }

    getFrettedNotesSvg(data) {
        let frettedNotes = '';
        let firstInstance = true;
        for (let [index, dataPoint] of data.entries()) {
            let stringPosition = index * this.stringSpacing;
            if (dataPoint[0] !== 'O' && dataPoint[0] !== 'X') {
                let yPosition = (dataPoint[1] - 1) * this.fretSpacing + 78;
                if (firstInstance) {
                    firstInstance = false;
                    let fretIndicatorLeft = this.fretboardLeft - 30;
                    let fretIndicatorTop = yPosition + 5;
                    frettedNotes += `<text x="${fretIndicatorLeft}" y="${fretIndicatorTop}" fill="black">${dataPoint[1]}</text>`;
                }
                let fretLabel = '';
                if (dataPoint[0] == 'T'){
                    fretLabel = 'T';
                } else {
                    fretLabel = this.indicatorLabels[parseInt(dataPoint[0]) + 2];
                }
                frettedNotes += `<circle cx="${this.fretboardLeft + stringPosition}" cy="${yPosition}" r="12" stroke="black" stroke-width="1" fill="black" />
                <text x="${this.fretboardLeft + stringPosition - 4}" y="${yPosition + 5}" fill="white">${fretLabel}</text>`;
            }
        }
        return frettedNotes;
    }
}