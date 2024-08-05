document.addEventListener('DOMContentLoaded', function() {
    const alatSearch = document.getElementById('alatSearch');
    const dropdownList = document.getElementById('dropdownList');

    const formIds = [
        'excavatorForm', 'ampForm', 'asphaltFinisherForm', 'asphaltSprayerForm', 'chainsawForm',
        'bulldozerForm', 'airCompressorForm', 'concreteMixerForm', 'crane10Form', 'craneOnTrackForm',
        'craneOnTrack75_100TonForm', 'dumpTruckForm', 'truckSemiTrailerForm', 'generatingSetForm',
        'motorGraderForm', 'trackLoaderForm', 'wheelLoaderForm', 'threeWheelLoaderForm',
        'tandemRollerForm', 'pneumaticTireRollerForm', 'sheepsfootRollerForm', 'vibratoryRollerForm',
        'concreteVibratorForm', 'waterPumpForm', 'jackHammerForm', 'blendingEquipmentForm',
        'asphaltLiquidMixerForm', 'pedestrianRollerForm', 'tamperForm', 'vibratingRammerForm',
        'pulviMixerForm', 'concretePumpForm', 'pileDriverHammerForm', 'weldingSetForm',
        'boredPileDrillingForm', 'roadMillingForm', 'rockDrillBreakerForm', 'coldRecyclerForm',
        'hotRecyclerForm', 'aggregateSpreaderForm', 'asphaltDistributorForm', 'concretePavingMachineForm',
        'batchingPlantForm', 'concreteBreakerForm', 'asphaltTankTruckForm', 'cementTankTruckForm',
        'concreteTruckMixerForm', 'borePileMachine60Form', 'aplikatorCatThermoplasticForm',
        'kapalTongkangForm', 'forkLiftForm', 'concreteCutterForm', 'powerBroomForm', 'asphaltSlurrySealTruckForm',
        'truckMixerAgitatorForm', 'selfPropelledMixerForm', 'stressingJackForm', 'groutingPumpForm',
        'trailerTronton30tForm', 'pontonForm', 'boilerForm', 'drumMixerForm', 'hcaForm', 'siliconSealPumpForm',
        'kunciTorsiForm', 'gerindaTanganForm', 'waterJetBlastingForm', 'handMixerForm', 'mesinBorForm','mesinAmplasKayuForm',
        'stamperForm', 'liftBarang1Form', 'liftBarang2Form', 'liftBarang3Form', 'crane1Form', 'craneTower2Form',
        'craneTower3Form', 'flat_bed_truckForm'
    ];

    const alatData = [
        'Excavator', 'Asphalt Mixing Plant (AMP)', 'Asphalt Finisher (Asphalt Paving Machine)', 'Asphalt Sprayer (Hand Sprayer)',
        'Chainsaw', 'Bulldozer', 'Air Compressor', 'Concrete Mixer', 'Crane (10-15 ton)', 'Crane On Track (Crawler Crane) 75 Ton',
        'Crane On Track 75-100 ton', 'Dump Truck', 'Truck Semi Trailer 15 ton', 'Generating Set (Genset)', 'Motor Grader',
        'Track Loader', 'Wheel Loader', 'Three Wheel Loader (TWR/Macadam Roller)', 'Tandem Roller', 'Pneumatic Tire Roller',
        'Sheepsfoot Roller', 'Vibratory Roller', 'Concrete Vibrator', 'Water Pump', 'Jack Hammer', 'Blending Equipment',
        'Asphalt Liquid Mixer', 'Pedestrian Roller', 'Tamper', 'Vibrating Rammer', 'Pulvi Mixer (Soil Stabilizer)', 'Concrete Pump',
        'Pile Driver-Hammer', 'Welding Set', 'Bored Pile Drilling Machine Max. dia. 2 m', 'Road Milling Machine', 'Rock Drill Breaker',
        'Cold Recycler', 'Hot Recycler', 'Aggregate Spreader', 'Asphalt Distributor', 'Concrete Paving Machine', 'Batching Plant (Concrete Pan Mixer)',
        'Concrete Breaker (Drop Hammer)', 'Asphalt Tank Truck', 'Cement Tank Truck', 'Concrete Truck Mixer', 'Bore Pile Machine dia. 60 cm',
        'Aplikator Cat Marka Jalan Thermoplastic', 'Kapal Tongkang/Perahu', 'Fork Lift', 'Concrete Cutter', 'Power Broom', 'Asphalt Slurry Seal Truck',
        'Truck Mixer Agitator', 'Self Propelled Mixer', 'Stressing Jack', 'Grouting Pump', 'Trailer Tronton 30 T', 'Ponton + Tug Boat',
        'Pre Heater/ Boiler', 'Drum Mixer Khusus', 'Hot Compressor Air Lance (HCA)', 'Silicon Seal Pump', 'Kunci Torsi (Torque Wrench)',
        'Gerinda Tangan', 'Water Jet Blasting', 'Hand Mixer', 'Mesin Bor', 'Mesin Amplas Kayu', 'Stamper', 'Lift Barang, Tinggi 6-10 lantai (20-40 m), Bm 1,0 ton',
        'Lift Barang, Tinggi 10-24 lantai (40-100 m), Bm 1,0 ton', 'Lift Barang, Tinggi 10-24 lantai (40-100 m), Bm 2,0 ton',
        'Crane (Stationary Stand By) 40 Ton', 'Crane (Tower), T=10-20 m, Arm 18 m, Bm 1,5 ton','Crane (Tower), T=20-40 m, Arm 30 m, Bm 2,5 ton', 'Flatbed Truck'
    ];

    const forms = {};

    alatData.forEach((alat, index) => {
        const elementId = formIds[index];
        if (elementId) {
            forms[alat] = document.getElementById(elementId);
        }
    });

    console.log(forms);

    alatSearch.addEventListener('input', function() {
        const value = alatSearch.value.toLowerCase();
        dropdownList.innerHTML = '';
        alatData.forEach(alat => {
            if (alat.toLowerCase().startsWith(value)) {
                const li = document.createElement('li');
                li.textContent = alat;
                li.addEventListener('click', function() {
                    alatSearch.value = alat;
                    dropdownList.innerHTML = '';
                    showForm(alat);
                });
                dropdownList.appendChild(li);
            }
        });
        dropdownList.classList.remove('hidden');
    });

    document.addEventListener('click', function(e) {
        if (!dropdownList.contains(e.target) && e.target !== alatSearch) {
            dropdownList.classList.add('hidden');
        }
    });

    function showForm(alat) {
        Object.values(forms).forEach(form => form.classList.add('hidden'));
        if (forms[alat]) {
            forms[alat].classList.remove('hidden');
        }
    }

    
    document.getElementById('opsi_crane1').addEventListener('change', toggleCraneFields);
    document.getElementById('opsi_crane2').addEventListener('change', toggleCraneFields2);
    document.getElementById('opsi_crane3').addEventListener('change', toggleCraneFields3);
    function toggleCraneFields() {
        const opsi = document.getElementById('opsi_crane1').value;
        const craneFields = document.getElementById('craneFields');
        const lokasiFields = document.getElementById('lokasiFields');
        const lantaiFields = document.getElementById('lantaiFields');
        
        craneFields.classList.remove('hidden');
        lokasiFields.classList.toggle('hidden', opsi !== 'lokasi');
        lantaiFields.classList.toggle('hidden', opsi !== 'lantai');
    }
    function toggleCraneFields2() {
        const opsi = document.getElementById('opsi_crane2').value;
        const craneFields = document.getElementById('craneTowerFields');
        const lokasiFields = document.getElementById('lokasiCrane2Fields');
        const lantaiFields = document.getElementById('lantaiCrane2Fields');
        
        craneFields.classList.remove('hidden');
        lokasiFields.classList.toggle('hidden', opsi !== 'lokasi');
        lantaiFields.classList.toggle('hidden', opsi !== 'lantai');
    }
    function toggleCraneFields3() {
        const opsi = document.getElementById('opsi_crane3').value;
        const craneFields = document.getElementById('craneTowerFields');
        const lokasiFields = document.getElementById('lokasiCrane3Fields');
        const lantaiFields = document.getElementById('lantaiCrane3Fields');
        
        craneFields.classList.remove('hidden');
        lokasiFields.classList.toggle('hidden', opsi !== 'lokasi');
        lantaiFields.classList.toggle('hidden', opsi !== 'lantai');
    }


    document.getElementById('calcForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const resultContainer = document.getElementById('resultContainer');
            resultContainer.innerHTML = ''; // Clear previous results

            if (data.error) {
                resultContainer.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                const resultsList = document.createElement('ul');
                for (const [key, value] of Object.entries(data)) {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${key}: ${value}`;
                    resultsList.appendChild(listItem);
                }
                resultContainer.appendChild(resultsList);
            }

            resultContainer.classList.remove('hidden');
        })
        .catch(error => console.error('Error:', error));
    });

    
});
